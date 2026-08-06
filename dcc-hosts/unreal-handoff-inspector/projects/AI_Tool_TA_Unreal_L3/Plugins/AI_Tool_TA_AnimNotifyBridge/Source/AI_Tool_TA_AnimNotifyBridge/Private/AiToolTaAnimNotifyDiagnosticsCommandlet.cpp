#include "AiToolTaAnimNotifyDiagnosticsCommandlet.h"

#include "AiToolTaAnimNotifyBridgeLibrary.h"
#include "Animation/AnimSequence.h"
#include "Dom/JsonObject.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/PackageName.h"
#include "Misc/Parse.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

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

void AddUniqueString(TArray<FString>& Rows, const FString& Value)
{
    if (!Value.IsEmpty())
    {
        Rows.AddUnique(Value);
    }
}

void CollectAssetPathsFromJsonObject(const TSharedPtr<FJsonObject>& Object, TArray<FString>& OutAssetPaths)
{
    if (!Object.IsValid())
    {
        return;
    }

    const TArray<TSharedPtr<FJsonValue>>* AnimationPaths = nullptr;
    if (Object->TryGetArrayField(TEXT("animationAssetPaths"), AnimationPaths) && AnimationPaths)
    {
        for (const TSharedPtr<FJsonValue>& Value : *AnimationPaths)
        {
            AddUniqueString(OutAssetPaths, Value.IsValid() ? Value->AsString() : FString());
        }
    }

    const TArray<TSharedPtr<FJsonValue>>* Intents = nullptr;
    if (Object->TryGetArrayField(TEXT("intents"), Intents) && Intents)
    {
        for (const TSharedPtr<FJsonValue>& Value : *Intents)
        {
            CollectAssetPathsFromJsonObject(Value.IsValid() ? Value->AsObject() : nullptr, OutAssetPaths);
        }
    }

    const TSharedPtr<FJsonObject>* Facts = nullptr;
    if (Object->TryGetObjectField(TEXT("facts"), Facts) && Facts)
    {
        CollectAssetPathsFromJsonObject(*Facts, OutAssetPaths);
    }
}

bool WriteOutput(const FString& OutputPath, const TSharedPtr<FJsonObject>& Payload)
{
    if (OutputPath.IsEmpty())
    {
        return true;
    }
    FString Text;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Text);
    if (!FJsonSerializer::Serialize(Payload.ToSharedRef(), Writer))
    {
        return false;
    }
    return FFileHelper::SaveStringToFile(Text, *OutputPath);
}

TSharedPtr<FJsonObject> DiagnosticToJson(const FAiToolTaAnimNotifyDiagnosticRow& Row)
{
    TSharedPtr<FJsonObject> Object = MakeShared<FJsonObject>();
    Object->SetStringField(TEXT("animSequencePath"), Row.AnimSequencePath);
    Object->SetStringField(TEXT("notifyName"), Row.NotifyName.ToString());
    Object->SetStringField(TEXT("notifyClass"), Row.NotifyClass);
    Object->SetStringField(TEXT("notifyStateClass"), Row.NotifyStateClass);
    Object->SetNumberField(TEXT("triggerTime"), Row.TriggerTime);
    Object->SetNumberField(TEXT("endTriggerTime"), Row.EndTriggerTime);
    Object->SetNumberField(TEXT("duration"), Row.Duration);
    Object->SetNumberField(TEXT("trackIndex"), Row.TrackIndex);
    return Object;
}
}

UAiToolTaAnimNotifyDiagnosticsCommandlet::UAiToolTaAnimNotifyDiagnosticsCommandlet()
{
    IsClient = false;
    IsEditor = true;
    IsServer = false;
    LogToConsole = true;
}

int32 UAiToolTaAnimNotifyDiagnosticsCommandlet::Main(const FString& Params)
{
    FString InputPath;
    FString OutputPath;
    FString SingleAnimPath;
    FParse::Value(*Params, TEXT("Input="), InputPath);
    FParse::Value(*Params, TEXT("Output="), OutputPath);
    FParse::Value(*Params, TEXT("AnimPath="), SingleAnimPath);

    UE_LOG(LogTemp, Display, TEXT("AI Tool TA Anim Notify Diagnostics Commandlet loaded."));
    UE_LOG(LogTemp, Display, TEXT("Input=%s Output=%s AnimPath=%s"), *InputPath, *OutputPath, *SingleAnimPath);

    TSharedPtr<FJsonObject> Output = MakeShared<FJsonObject>();
    Output->SetStringField(TEXT("schema"), TEXT("ai-tool-ta-anim-notify-diagnostics@0.1.0"));
    Output->SetStringField(TEXT("input"), InputPath);
    Output->SetStringField(TEXT("singleAnimPath"), SingleAnimPath);
    Output->SetNumberField(TEXT("assetWrites"), 0);
    Output->SetNumberField(TEXT("engineWrites"), 0);
    Output->SetNumberField(TEXT("productionWrites"), 0);

    TArray<FString> AssetPaths;
    AddUniqueString(AssetPaths, SingleAnimPath);

    if (!InputPath.IsEmpty())
    {
        FString InputText;
        if (!FFileHelper::LoadFileToString(InputText, *InputPath))
        {
            Output->SetStringField(TEXT("status"), TEXT("blocked_by_missing_input_report"));
            Output->SetStringField(TEXT("message"), TEXT("Input report could not be read."));
            WriteOutput(OutputPath, Output);
            UE_LOG(LogTemp, Error, TEXT("Input report could not be read: %s"), *InputPath);
            return 3;
        }

        TSharedPtr<FJsonObject> InputObject;
        TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(InputText);
        if (!FJsonSerializer::Deserialize(Reader, InputObject) || !InputObject.IsValid())
        {
            Output->SetStringField(TEXT("status"), TEXT("blocked_by_invalid_input_json"));
            Output->SetStringField(TEXT("message"), TEXT("Input report is not valid JSON."));
            WriteOutput(OutputPath, Output);
            UE_LOG(LogTemp, Error, TEXT("Input report is not valid JSON: %s"), *InputPath);
            return 4;
        }
        CollectAssetPathsFromJsonObject(InputObject, AssetPaths);
    }

    Output->SetNumberField(TEXT("requestedAnimSequencePaths"), AssetPaths.Num());
    if (AssetPaths.IsEmpty())
    {
        Output->SetStringField(TEXT("status"), TEXT("readiness_invocation_only"));
        Output->SetStringField(TEXT("message"), TEXT("No AnimSequence paths supplied; commandlet visibility is proven."));
        WriteOutput(OutputPath, Output);
        return 0;
    }

    TArray<TSharedPtr<FJsonValue>> AssetRows;
    int32 LoadedSequences = 0;
    int32 NotifyRows = 0;
    for (const FString& AssetPath : AssetPaths)
    {
        TSharedPtr<FJsonObject> AssetRow = MakeShared<FJsonObject>();
        AssetRow->SetStringField(TEXT("assetPath"), AssetPath);
        AssetRow->SetStringField(TEXT("objectPath"), ToObjectPath(AssetPath));

        UAnimSequence* AnimSequence = LoadObject<UAnimSequence>(nullptr, *ToObjectPath(AssetPath));
        AssetRow->SetBoolField(TEXT("loaded"), AnimSequence != nullptr);
        if (!AnimSequence)
        {
            AssetRow->SetStringField(TEXT("status"), TEXT("blocked_by_missing_animsequence"));
            AssetRows.Add(MakeShared<FJsonValueObject>(AssetRow));
            continue;
        }

        LoadedSequences++;
        TArray<FAiToolTaAnimNotifyDiagnosticRow> Diagnostics;
        FString Message;
        const bool bCollected = UAiToolTaAnimNotifyBridgeLibrary::CollectAnimNotifyDiagnostics(AnimSequence, Diagnostics, Message);
        AssetRow->SetBoolField(TEXT("collected"), bCollected);
        AssetRow->SetStringField(TEXT("message"), Message);
        AssetRow->SetNumberField(TEXT("notifyCount"), Diagnostics.Num());
        NotifyRows += Diagnostics.Num();

        TArray<TSharedPtr<FJsonValue>> DiagnosticValues;
        for (const FAiToolTaAnimNotifyDiagnosticRow& Diagnostic : Diagnostics)
        {
            DiagnosticValues.Add(MakeShared<FJsonValueObject>(DiagnosticToJson(Diagnostic)));
        }
        AssetRow->SetArrayField(TEXT("notifies"), DiagnosticValues);
        AssetRows.Add(MakeShared<FJsonValueObject>(AssetRow));
    }

    Output->SetArrayField(TEXT("assets"), AssetRows);
    Output->SetNumberField(TEXT("loadedSequences"), LoadedSequences);
    Output->SetNumberField(TEXT("notifyRows"), NotifyRows);
    Output->SetStringField(TEXT("status"), TEXT("diagnostics_completed"));
    WriteOutput(OutputPath, Output);
    UE_LOG(LogTemp, Display, TEXT("Anim notify diagnostics completed. assets=%d loaded=%d notifyRows=%d"), AssetPaths.Num(), LoadedSequences, NotifyRows);
    return 0;
}
