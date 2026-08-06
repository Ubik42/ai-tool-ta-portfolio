#include "AiToolTaControlRigBridgeLibrary.h"

#include "UObject/UnrealType.h"

namespace
{
bool IsInterestingName(const FString& Name)
{
    const FString Lower = Name.ToLower();
    return Lower.Contains(TEXT("compile"))
        || Lower.Contains(TEXT("diagnostic"))
        || Lower.Contains(TEXT("status"))
        || Lower.Contains(TEXT("message"))
        || Lower.Contains(TEXT("error"))
        || Lower.Contains(TEXT("warning"))
        || Lower.Contains(TEXT("log"));
}

bool InvokeNoArgFunction(UObject* Object, const TCHAR* FunctionName, FString& OutError)
{
    if (!Object)
    {
        OutError = TEXT("Missing object.");
        return false;
    }
    UFunction* Function = Object->FindFunction(FunctionName);
    if (!Function)
    {
        OutError = FString::Printf(TEXT("Function not found: %s"), FunctionName);
        return false;
    }
    if (Function->NumParms != 0)
    {
        OutError = FString::Printf(TEXT("Function requires parameters: %s"), FunctionName);
        return false;
    }
    Object->ProcessEvent(Function, nullptr);
    return true;
}
}

bool UAiToolTaControlRigBridgeLibrary::CollectControlRigDiagnostics(
    UObject* ControlRigBlueprint,
    TArray<FAiToolTaControlRigDiagnosticRow>& Rows,
    FString& Message)
{
    Rows.Reset();
    if (!ControlRigBlueprint)
    {
        Message = TEXT("Control Rig Blueprint is null.");
        return false;
    }

    FAiToolTaControlRigDiagnosticRow Row;
    Row.ControlRigPath = ControlRigBlueprint->GetPathName();
    Row.AssetClass = ControlRigBlueprint->GetClass() ? ControlRigBlueprint->GetClass()->GetName() : TEXT("None");
    Row.bAssetLoaded = true;

    for (TFieldIterator<UFunction> It(ControlRigBlueprint->GetClass(), EFieldIteratorFlags::IncludeSuper); It; ++It)
    {
        const FString FunctionName = It->GetName();
        if (!IsInterestingName(FunctionName))
        {
            continue;
        }
        if (FunctionName.ToLower().Contains(TEXT("compile")))
        {
            Row.CompileMethodCount += 1;
        }
        else
        {
            Row.DiagnosticMethodCount += 1;
        }
    }

    for (TFieldIterator<FProperty> It(ControlRigBlueprint->GetClass(), EFieldIteratorFlags::IncludeSuper); It; ++It)
    {
        const FString PropertyName = It->GetName();
        if (!IsInterestingName(PropertyName))
        {
            continue;
        }
        FString ValueText;
        It->ExportText_InContainer(0, ValueText, ControlRigBlueprint, ControlRigBlueprint, ControlRigBlueprint, PPF_None);
        if (!ValueText.IsEmpty())
        {
            Row.ReadablePropertyCount += 1;
            if (PropertyName.ToLower().Contains(TEXT("status")) || PropertyName.ToLower().Contains(TEXT("diagnostic")))
            {
                Row.bDirectStatusReadable = true;
            }
        }
    }

    FString CompileError;
    Row.bCompileInvoked = InvokeNoArgFunction(ControlRigBlueprint, TEXT("RecompileVMIfRequired"), CompileError)
        || InvokeNoArgFunction(ControlRigBlueprint, TEXT("RecompileVM"), CompileError);
    Row.bCompileSucceeded = Row.bCompileInvoked;
    Row.Message = Row.bCompileSucceeded ? TEXT("Control Rig diagnostic reflection completed.") : CompileError;
    Message = Row.Message;
    Rows.Add(Row);
    return Row.bAssetLoaded;
}
