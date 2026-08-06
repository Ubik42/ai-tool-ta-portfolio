#include "AiToolTaControlRigDiagnosticsCommandlet.h"

#include "AiToolTaControlRigBridgeLibrary.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Commandlets/Commandlet.h"
#include "Dom/JsonObject.h"
#include "Dom/JsonValue.h"
#include "HAL/FileManager.h"
#include "JsonObjectConverter.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/PackageName.h"
#include "Misc/Parse.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

UAiToolTaControlRigDiagnosticsCommandlet::UAiToolTaControlRigDiagnosticsCommandlet()
{
    IsClient = false;
    IsEditor = true;
    LogToConsole = true;
}

namespace
{
FString ToObjectPath(const FString& AssetPath)
{
    if (AssetPath.Contains(TEXT(".")))
    {
        return AssetPath;
    }
    return FString::Printf(TEXT("%s.%s"), *AssetPath, *FPackageName::GetLongPackageAssetName(AssetPath));
}

bool WriteOutput(const FString& OutputPath, const TSharedPtr<FJsonObject>& Payload)
{
    if (OutputPath.IsEmpty())
    {
        return true;
    }
    FString Text;
    const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Text);
    FJsonSerializer::Serialize(Payload.ToSharedRef(), Writer);
    return FFileHelper::SaveStringToFile(Text, *OutputPath);
}
}

int32 UAiToolTaControlRigDiagnosticsCommandlet::Main(const FString& Params)
{
    UE_LOG(LogTemp, Display, TEXT("AI Tool TA Control Rig Diagnostics commandlet entered."));

    FString OutputPath;
    FParse::Value(*Params, TEXT("Output="), OutputPath);
    FString ControlRigPath;
    FParse::Value(*Params, TEXT("ControlRig="), ControlRigPath);

    TSharedPtr<FJsonObject> Payload = MakeShared<FJsonObject>();
    Payload->SetStringField(TEXT("schema"), TEXT("ai-tool-ta-control-rig-diagnostics-result@0.1.0"));
    Payload->SetStringField(TEXT("controlRigPath"), ControlRigPath);
    Payload->SetBoolField(TEXT("readinessInvocation"), ControlRigPath.IsEmpty());
    Payload->SetNumberField(TEXT("assetWrites"), 0);
    Payload->SetNumberField(TEXT("engineWrites"), 0);
    Payload->SetNumberField(TEXT("productionWrites"), 0);

    if (ControlRigPath.IsEmpty())
    {
        Payload->SetStringField(TEXT("status"), TEXT("readiness_invocation_only"));
        WriteOutput(OutputPath, Payload);
        return 0;
    }

    UObject* ControlRig = LoadObject<UObject>(nullptr, *ToObjectPath(ControlRigPath));
    TArray<FAiToolTaControlRigDiagnosticRow> Rows;
    FString Message;
    const bool bCollected = UAiToolTaControlRigBridgeLibrary::CollectControlRigDiagnostics(ControlRig, Rows, Message);
    Payload->SetBoolField(TEXT("targetLoaded"), ControlRig != nullptr);
    Payload->SetBoolField(TEXT("diagnosticsCollected"), bCollected);
    Payload->SetStringField(TEXT("message"), Message);
    Payload->SetStringField(TEXT("status"), bCollected ? TEXT("diagnostics_completed") : TEXT("diagnostics_blocked"));

    TArray<TSharedPtr<FJsonValue>> JsonRows;
    for (const FAiToolTaControlRigDiagnosticRow& Row : Rows)
    {
        TSharedPtr<FJsonObject> JsonRow = MakeShared<FJsonObject>();
        JsonRow->SetStringField(TEXT("controlRigPath"), Row.ControlRigPath);
        JsonRow->SetStringField(TEXT("assetClass"), Row.AssetClass);
        JsonRow->SetBoolField(TEXT("assetLoaded"), Row.bAssetLoaded);
        JsonRow->SetNumberField(TEXT("compileMethodCount"), Row.CompileMethodCount);
        JsonRow->SetNumberField(TEXT("diagnosticMethodCount"), Row.DiagnosticMethodCount);
        JsonRow->SetNumberField(TEXT("readablePropertyCount"), Row.ReadablePropertyCount);
        JsonRow->SetBoolField(TEXT("compileInvoked"), Row.bCompileInvoked);
        JsonRow->SetBoolField(TEXT("compileSucceeded"), Row.bCompileSucceeded);
        JsonRow->SetBoolField(TEXT("directStatusReadable"), Row.bDirectStatusReadable);
        JsonRow->SetStringField(TEXT("message"), Row.Message);
        JsonRows.Add(MakeShared<FJsonValueObject>(JsonRow));
    }
    Payload->SetArrayField(TEXT("rows"), JsonRows);
    WriteOutput(OutputPath, Payload);
    return bCollected ? 0 : 2;
}
