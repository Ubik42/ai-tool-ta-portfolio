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
#include "UObject/Package.h"
#include "UObject/SavePackage.h"

namespace
{
struct FNotifyRequest
{
    FString AnimSequencePath;
    FName NotifyName;
    float TriggerTime = 0.0f;
    int32 TrackIndex = 0;
    FString IntentId;
    FString AssetId;
    FString SlotRole;
    FString SourceReceiptId;
};

FString ToPackagePath(const FString& AssetPath)
{
    int32 SlashIndex = INDEX_NONE;
    AssetPath.FindLastChar(TEXT('/'), SlashIndex);
    int32 DotIndex = INDEX_NONE;
    if (AssetPath.FindLastChar(TEXT('.'), DotIndex) && DotIndex > SlashIndex)
    {
        return AssetPath.Left(DotIndex);
    }
    return AssetPath;
}

FString ToObjectPath(const FString& AssetPath)
{
    const FString PackagePath = ToPackagePath(AssetPath);
    if (PackagePath.Contains(TEXT(".")))
    {
        return PackagePath;
    }
    return FString::Printf(TEXT("%s.%s"), *PackagePath, *FPackageName::GetLongPackageAssetName(PackagePath));
}

void AddUniqueString(TArray<FString>& Rows, const FString& Value)
{
    if (!Value.IsEmpty())
    {
        Rows.AddUnique(ToPackagePath(Value));
    }
}

bool ReadJsonNumber(const TSharedPtr<FJsonObject>& Object, const TCHAR* FieldName, double& OutValue)
{
    if (!Object.IsValid())
    {
        return false;
    }
    return Object->TryGetNumberField(FieldName, OutValue);
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

    const TArray<TSharedPtr<FJsonValue>>* Requests = nullptr;
    if (Object->TryGetArrayField(TEXT("requests"), Requests) && Requests)
    {
        for (const TSharedPtr<FJsonValue>& Value : *Requests)
        {
            const TSharedPtr<FJsonObject> RequestObject = Value.IsValid() ? Value->AsObject() : nullptr;
            if (!RequestObject.IsValid())
            {
                continue;
            }
            FString RequestAnimPath;
            if (!RequestObject->TryGetStringField(TEXT("animSequencePath"), RequestAnimPath))
            {
                RequestObject->TryGetStringField(TEXT("assetPath"), RequestAnimPath);
            }
            AddUniqueString(OutAssetPaths, RequestAnimPath);
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

TArray<FNotifyRequest> CollectNotifyRequestsFromJsonObject(const TSharedPtr<FJsonObject>& Object)
{
    TArray<FNotifyRequest> Requests;
    if (!Object.IsValid())
    {
        return Requests;
    }

    const TArray<TSharedPtr<FJsonValue>>* RequestValues = nullptr;
    if (!Object->TryGetArrayField(TEXT("requests"), RequestValues) || !RequestValues)
    {
        return Requests;
    }

    for (const TSharedPtr<FJsonValue>& Value : *RequestValues)
    {
        const TSharedPtr<FJsonObject> RequestObject = Value.IsValid() ? Value->AsObject() : nullptr;
        if (!RequestObject.IsValid())
        {
            continue;
        }

        FString AnimSequencePath;
        FString NotifyName;
        if (!RequestObject->TryGetStringField(TEXT("animSequencePath"), AnimSequencePath))
        {
            RequestObject->TryGetStringField(TEXT("assetPath"), AnimSequencePath);
        }
        if (!RequestObject->TryGetStringField(TEXT("notifyName"), NotifyName))
        {
            RequestObject->TryGetStringField(TEXT("eventName"), NotifyName);
        }

        if (AnimSequencePath.IsEmpty() || NotifyName.IsEmpty())
        {
            continue;
        }

        FNotifyRequest Request;
        Request.AnimSequencePath = ToPackagePath(AnimSequencePath);
        Request.NotifyName = FName(*NotifyName);
        double TriggerTime = 0.0;
        if (ReadJsonNumber(RequestObject, TEXT("triggerTime"), TriggerTime))
        {
            Request.TriggerTime = static_cast<float>(TriggerTime);
        }
        double TrackIndex = 0.0;
        if (ReadJsonNumber(RequestObject, TEXT("trackIndex"), TrackIndex))
        {
            Request.TrackIndex = FMath::Max(0, static_cast<int32>(TrackIndex));
        }
        RequestObject->TryGetStringField(TEXT("intentId"), Request.IntentId);
        RequestObject->TryGetStringField(TEXT("assetId"), Request.AssetId);
        RequestObject->TryGetStringField(TEXT("slotRole"), Request.SlotRole);
        RequestObject->TryGetStringField(TEXT("sourceReceiptId"), Request.SourceReceiptId);
        Requests.Add(Request);
    }

    return Requests;
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

bool SaveAnimSequencePackage(UAnimSequence* AnimSequence, FString& OutPackageFilename)
{
    if (!AnimSequence)
    {
        return false;
    }
    UPackage* Package = AnimSequence->GetOutermost();
    if (!Package)
    {
        return false;
    }
    if (!FPackageName::TryConvertLongPackageNameToFilename(Package->GetName(), OutPackageFilename, FPackageName::GetAssetPackageExtension()))
    {
        return false;
    }
    FSavePackageArgs SaveArgs;
    SaveArgs.TopLevelFlags = RF_Public | RF_Standalone;
    SaveArgs.SaveFlags = SAVE_NoError;
    return UPackage::SavePackage(Package, AnimSequence, *OutPackageFilename, SaveArgs);
}

bool MatchesRequest(const FAnimNotifyEvent& Event, const FNotifyRequest& Request)
{
    return !Event.IsBlueprintNotify()
        && Event.NotifyName == Request.NotifyName
        && FMath::Abs(Event.GetTriggerTime() - Request.TriggerTime) <= 0.05f;
}

bool HasRequestedNotify(UAnimSequence* AnimSequence, const FNotifyRequest& Request)
{
    if (!AnimSequence)
    {
        return false;
    }
    for (const FAnimNotifyEvent& Event : AnimSequence->Notifies)
    {
        if (MatchesRequest(Event, Request))
        {
            return true;
        }
    }
    return false;
}

int32 CountRequestedNotifies(UAnimSequence* AnimSequence, const TArray<FNotifyRequest>& Requests)
{
    int32 Count = 0;
    for (const FNotifyRequest& Request : Requests)
    {
        if (HasRequestedNotify(AnimSequence, Request))
        {
            Count++;
        }
    }
    return Count;
}

bool AddNamedNotify(UAnimSequence* AnimSequence, const FNotifyRequest& Request)
{
    if (!AnimSequence || Request.NotifyName.IsNone())
    {
        return false;
    }

    const float PlayLength = FMath::Max(AnimSequence->GetPlayLength(), 0.0f);
    const float ClampedTriggerTime = FMath::Clamp(Request.TriggerTime, 0.0f, FMath::Max(PlayLength - KINDA_SMALL_NUMBER, 0.0f));

    AnimSequence->Modify();
    FAnimNotifyEvent& NewEvent = AnimSequence->Notifies.AddDefaulted_GetRef();
    NewEvent.NotifyName = Request.NotifyName;
    NewEvent.Link(AnimSequence, ClampedTriggerTime);
    NewEvent.TriggerTimeOffset = GetTriggerTimeOffsetForType(AnimSequence->CalculateOffsetForNotify(ClampedTriggerTime));
    NewEvent.TrackIndex = FMath::Max(0, Request.TrackIndex);
    NewEvent.Notify = nullptr;
    NewEvent.NotifyStateClass = nullptr;
#if WITH_EDITORONLY_DATA
    NewEvent.Guid = FGuid::NewGuid();
#endif
    AnimSequence->MarkPackageDirty();
    AnimSequence->RefreshCacheData();
    return true;
}

int32 RemoveCreatedNotifies(UAnimSequence* AnimSequence, const TArray<FNotifyRequest>& Requests)
{
    if (!AnimSequence)
    {
        return 0;
    }

    int32 Removed = 0;
    for (const FNotifyRequest& Request : Requests)
    {
        for (int32 Index = AnimSequence->Notifies.Num() - 1; Index >= 0; --Index)
        {
            if (MatchesRequest(AnimSequence->Notifies[Index], Request))
            {
                AnimSequence->Notifies.RemoveAt(Index);
                Removed++;
                break;
            }
        }
    }

    if (Removed > 0)
    {
        AnimSequence->MarkPackageDirty();
        AnimSequence->RefreshCacheData();
    }
    return Removed;
}

TSharedPtr<FJsonObject> RequestToJson(const FNotifyRequest& Request)
{
    TSharedPtr<FJsonObject> Object = MakeShared<FJsonObject>();
    Object->SetStringField(TEXT("animSequencePath"), Request.AnimSequencePath);
    Object->SetStringField(TEXT("notifyName"), Request.NotifyName.ToString());
    Object->SetNumberField(TEXT("triggerTime"), Request.TriggerTime);
    Object->SetNumberField(TEXT("trackIndex"), Request.TrackIndex);
    Object->SetStringField(TEXT("intentId"), Request.IntentId);
    Object->SetStringField(TEXT("assetId"), Request.AssetId);
    Object->SetStringField(TEXT("slotRole"), Request.SlotRole);
    Object->SetStringField(TEXT("sourceReceiptId"), Request.SourceReceiptId);
    return Object;
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

TArray<TSharedPtr<FJsonValue>> DiagnosticsToJson(UAnimSequence* AnimSequence, int32& OutNotifyRows)
{
    TArray<TSharedPtr<FJsonValue>> DiagnosticValues;
    OutNotifyRows = 0;
    if (!AnimSequence)
    {
        return DiagnosticValues;
    }

    TArray<FAiToolTaAnimNotifyDiagnosticRow> Diagnostics;
    FString Message;
    UAiToolTaAnimNotifyBridgeLibrary::CollectAnimNotifyDiagnostics(AnimSequence, Diagnostics, Message);
    OutNotifyRows = Diagnostics.Num();
    for (const FAiToolTaAnimNotifyDiagnosticRow& Diagnostic : Diagnostics)
    {
        DiagnosticValues.Add(MakeShared<FJsonValueObject>(DiagnosticToJson(Diagnostic)));
    }
    return DiagnosticValues;
}

int32 RunAuthoringMode(
    const TSharedPtr<FJsonObject>& InputObject,
    const FString& InputPath,
    const FString& OutputPath,
    bool bApply,
    bool bRollback,
    bool bAllowPublicFixtureWrite)
{
    TSharedPtr<FJsonObject> Output = MakeShared<FJsonObject>();
    Output->SetStringField(TEXT("schema"), TEXT("ai-tool-ta-anim-notify-authoring-result@0.1.0"));
    Output->SetStringField(TEXT("input"), InputPath);
    Output->SetBoolField(TEXT("apply"), bApply);
    Output->SetBoolField(TEXT("rollback"), bRollback);
    Output->SetBoolField(TEXT("allowPublicFixtureWrite"), bAllowPublicFixtureWrite);
    Output->SetNumberField(TEXT("assetWrites"), 0);
    Output->SetNumberField(TEXT("engineWrites"), 0);
    Output->SetNumberField(TEXT("productionWrites"), 0);
    Output->SetNumberField(TEXT("inMemoryWrites"), 0);

    const TArray<FNotifyRequest> Requests = CollectNotifyRequestsFromJsonObject(InputObject);
    Output->SetNumberField(TEXT("requestCount"), Requests.Num());
    if (Requests.IsEmpty())
    {
        Output->SetStringField(TEXT("status"), TEXT("blocked_by_missing_notify_requests"));
        Output->SetStringField(TEXT("message"), TEXT("Input receipt has no valid requests array."));
        WriteOutput(OutputPath, Output);
        UE_LOG(LogTemp, Error, TEXT("Input receipt has no valid notify requests: %s"), *InputPath);
        return 6;
    }
    if (bApply && !bAllowPublicFixtureWrite)
    {
        Output->SetStringField(TEXT("status"), TEXT("blocked_by_missing_public_fixture_write_guard"));
        Output->SetStringField(TEXT("message"), TEXT("Apply mode requires -AllowPublicFixtureWrite."));
        WriteOutput(OutputPath, Output);
        UE_LOG(LogTemp, Warning, TEXT("Apply mode requires -AllowPublicFixtureWrite."));
        return 2;
    }
    if (bApply && !bRollback)
    {
        Output->SetStringField(TEXT("status"), TEXT("blocked_by_missing_rollback_guard"));
        Output->SetStringField(TEXT("message"), TEXT("Public portfolio execution requires -Rollback so no persistent mutation remains."));
        WriteOutput(OutputPath, Output);
        UE_LOG(LogTemp, Warning, TEXT("Public portfolio execution requires -Rollback."));
        return 10;
    }

    TMap<FString, TArray<FNotifyRequest>> RequestsByAsset;
    for (const FNotifyRequest& Request : Requests)
    {
        const bool bPublicFixtureTarget = Request.AnimSequencePath.StartsWith(TEXT("/Game/AI_Tool_TA/"));
        if (bApply && !bPublicFixtureTarget)
        {
            Output->SetStringField(TEXT("status"), TEXT("blocked_by_non_public_fixture_target"));
            Output->SetStringField(TEXT("message"), FString::Printf(TEXT("Apply mode is limited to /Game/AI_Tool_TA assets: %s"), *Request.AnimSequencePath));
            WriteOutput(OutputPath, Output);
            UE_LOG(LogTemp, Warning, TEXT("Apply mode is limited to /Game/AI_Tool_TA assets: %s"), *Request.AnimSequencePath);
            return 9;
        }
        RequestsByAsset.FindOrAdd(Request.AnimSequencePath).Add(Request);
    }

    TArray<TSharedPtr<FJsonValue>> AssetRows;
    int32 LoadedSequences = 0;
    int32 AlreadyPresent = 0;
    int32 WouldCreate = 0;
    int32 Applied = 0;
    int32 PostCheckPresent = 0;
    int32 RollbackRemoved = 0;
    int32 PostRollbackPresent = 0;
    int32 AssetWrites = 0;
    int32 InMemoryWrites = 0;
    bool bAllAssetsLoaded = true;
    bool bAllSavesOk = true;

    for (const TPair<FString, TArray<FNotifyRequest>>& Pair : RequestsByAsset)
    {
        const FString& AssetPath = Pair.Key;
        const TArray<FNotifyRequest>& AssetRequests = Pair.Value;
        TSharedPtr<FJsonObject> AssetRow = MakeShared<FJsonObject>();
        AssetRow->SetStringField(TEXT("assetPath"), AssetPath);
        AssetRow->SetStringField(TEXT("objectPath"), ToObjectPath(AssetPath));
        AssetRow->SetNumberField(TEXT("requestCount"), AssetRequests.Num());
        AssetRow->SetBoolField(TEXT("publicFixtureTarget"), AssetPath.StartsWith(TEXT("/Game/AI_Tool_TA/")));

        UAnimSequence* AnimSequence = LoadObject<UAnimSequence>(nullptr, *ToObjectPath(AssetPath));
        AssetRow->SetBoolField(TEXT("loaded"), AnimSequence != nullptr);
        if (!AnimSequence)
        {
            bAllAssetsLoaded = false;
            AssetRow->SetStringField(TEXT("status"), TEXT("blocked_by_missing_animsequence"));
            AssetRows.Add(MakeShared<FJsonValueObject>(AssetRow));
            continue;
        }

        LoadedSequences++;
        const int32 PreExisting = CountRequestedNotifies(AnimSequence, AssetRequests);
        AssetRow->SetNumberField(TEXT("preExisting"), PreExisting);

        TArray<FNotifyRequest> CreatedRequests;
        TArray<TSharedPtr<FJsonValue>> ResultValues;
        for (const FNotifyRequest& Request : AssetRequests)
        {
            TSharedPtr<FJsonObject> Result = RequestToJson(Request);
            const bool bAlreadyPresent = HasRequestedNotify(AnimSequence, Request);
            Result->SetBoolField(TEXT("alreadyPresent"), bAlreadyPresent);
            Result->SetBoolField(TEXT("applied"), false);
            if (bAlreadyPresent)
            {
                AlreadyPresent++;
                Result->SetStringField(TEXT("message"), TEXT("Notify already exists on AnimSequence."));
            }
            else if (!bApply)
            {
                WouldCreate++;
                Result->SetStringField(TEXT("message"), TEXT("Notify would be created on AnimSequence."));
            }
            else
            {
                const bool bAdded = AddNamedNotify(AnimSequence, Request);
                Result->SetBoolField(TEXT("applied"), bAdded);
                Result->SetStringField(TEXT("message"), bAdded ? TEXT("Notify created on AnimSequence.") : TEXT("Notify creation failed."));
                if (bAdded)
                {
                    Applied++;
                    InMemoryWrites++;
                    CreatedRequests.Add(Request);
                }
            }
            ResultValues.Add(MakeShared<FJsonValueObject>(Result));
        }
        AssetRow->SetArrayField(TEXT("results"), ResultValues);

        if (!bApply)
        {
            int32 DiagnosticRows = 0;
            AssetRow->SetArrayField(TEXT("notifies"), DiagnosticsToJson(AnimSequence, DiagnosticRows));
            AssetRow->SetNumberField(TEXT("notifyCount"), DiagnosticRows);
            AssetRow->SetStringField(TEXT("status"), TEXT("dry_run_completed"));
            AssetRows.Add(MakeShared<FJsonValueObject>(AssetRow));
            continue;
        }

        const int32 AssetPostCheckPresent = CountRequestedNotifies(AnimSequence, AssetRequests);
        PostCheckPresent += AssetPostCheckPresent;
        AssetRow->SetNumberField(TEXT("postCheckPresent"), AssetPostCheckPresent);

        FString PackageFilename;
        bool bSavedAfterApply = true;
        if (CreatedRequests.Num() > 0)
        {
            bSavedAfterApply = SaveAnimSequencePackage(AnimSequence, PackageFilename);
            bAllSavesOk = bAllSavesOk && bSavedAfterApply;
            AssetWrites += bSavedAfterApply ? 1 : 0;
        }
        AssetRow->SetStringField(TEXT("packageFilename"), PackageFilename);
        AssetRow->SetBoolField(TEXT("savedAfterApply"), bSavedAfterApply);

        int32 AssetRollbackRemoved = 0;
        int32 AssetPostRollbackPresent = 0;
        bool bSavedAfterRollback = true;
        if (bRollback && CreatedRequests.Num() > 0)
        {
            AssetRollbackRemoved = RemoveCreatedNotifies(AnimSequence, CreatedRequests);
            AssetPostRollbackPresent = CountRequestedNotifies(AnimSequence, CreatedRequests);
            bSavedAfterRollback = SaveAnimSequencePackage(AnimSequence, PackageFilename);
            bAllSavesOk = bAllSavesOk && bSavedAfterRollback;
            AssetWrites += bSavedAfterRollback ? 1 : 0;
        }

        RollbackRemoved += AssetRollbackRemoved;
        PostRollbackPresent += AssetPostRollbackPresent;
        AssetRow->SetNumberField(TEXT("rollbackRemoved"), AssetRollbackRemoved);
        AssetRow->SetNumberField(TEXT("postRollbackPresent"), AssetPostRollbackPresent);
        AssetRow->SetBoolField(TEXT("savedAfterRollback"), bSavedAfterRollback);

        int32 FinalDiagnosticRows = 0;
        AssetRow->SetArrayField(TEXT("finalNotifies"), DiagnosticsToJson(AnimSequence, FinalDiagnosticRows));
        AssetRow->SetNumberField(TEXT("finalNotifyCount"), FinalDiagnosticRows);
        AssetRow->SetStringField(TEXT("status"), TEXT("apply_postcheck_rollback_completed"));
        AssetRows.Add(MakeShared<FJsonValueObject>(AssetRow));
    }

    Output->SetBoolField(TEXT("dryRun"), !bApply);
    Output->SetBoolField(TEXT("targetLoaded"), bAllAssetsLoaded && LoadedSequences == RequestsByAsset.Num());
    Output->SetNumberField(TEXT("assetCount"), RequestsByAsset.Num());
    Output->SetNumberField(TEXT("loadedSequences"), LoadedSequences);
    Output->SetNumberField(TEXT("alreadyPresent"), AlreadyPresent);
    Output->SetNumberField(TEXT("wouldCreate"), WouldCreate);
    Output->SetNumberField(TEXT("applied"), Applied);
    Output->SetNumberField(TEXT("postCheckPresent"), PostCheckPresent);
    Output->SetNumberField(TEXT("rollbackRemoved"), RollbackRemoved);
    Output->SetNumberField(TEXT("postRollbackPresent"), PostRollbackPresent);
    Output->SetNumberField(TEXT("assetWrites"), AssetWrites);
    Output->SetNumberField(TEXT("inMemoryWrites"), InMemoryWrites);
    Output->SetBoolField(TEXT("savedAfterApply"), bAllSavesOk);
    Output->SetBoolField(TEXT("savedAfterRollback"), bAllSavesOk);
    Output->SetBoolField(TEXT("persistentMutation"), PostRollbackPresent != 0);
    Output->SetArrayField(TEXT("assets"), AssetRows);

    if (!bApply)
    {
        Output->SetStringField(TEXT("status"), TEXT("dry_run_completed"));
        WriteOutput(OutputPath, Output);
        UE_LOG(LogTemp, Display, TEXT("Anim notify dry-run completed. assets=%d requests=%d wouldCreate=%d alreadyPresent=%d"), RequestsByAsset.Num(), Requests.Num(), WouldCreate, AlreadyPresent);
        return 0;
    }

    const bool bRollbackOk = bAllAssetsLoaded
        && bAllSavesOk
        && Applied == Requests.Num()
        && PostCheckPresent >= Requests.Num()
        && RollbackRemoved == Applied
        && PostRollbackPresent == 0;
    Output->SetStringField(TEXT("status"), bRollbackOk ? TEXT("apply_postcheck_rollback_completed") : TEXT("apply_postcheck_rollback_incomplete"));
    if (!WriteOutput(OutputPath, Output))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to write commandlet output: %s"), *OutputPath);
        return 8;
    }
    UE_LOG(LogTemp, Display, TEXT("Anim notify apply/post-check/rollback completed. assets=%d applied=%d postCheckPresent=%d rollbackRemoved=%d postRollbackPresent=%d"), RequestsByAsset.Num(), Applied, PostCheckPresent, RollbackRemoved, PostRollbackPresent);
    return bRollbackOk ? 0 : 12;
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
    const bool bApply = FParse::Param(*Params, TEXT("Apply"));
    const bool bRollback = FParse::Param(*Params, TEXT("Rollback"));
    const bool bAllowPublicFixtureWrite = FParse::Param(*Params, TEXT("AllowPublicFixtureWrite"));
    FParse::Value(*Params, TEXT("Input="), InputPath);
    FParse::Value(*Params, TEXT("Output="), OutputPath);
    FParse::Value(*Params, TEXT("AnimPath="), SingleAnimPath);

    UE_LOG(LogTemp, Display, TEXT("AI Tool TA Anim Notify Diagnostics Commandlet loaded."));
    UE_LOG(LogTemp, Display, TEXT("Input=%s Output=%s AnimPath=%s Apply=%s Rollback=%s AllowPublicFixtureWrite=%s"), *InputPath, *OutputPath, *SingleAnimPath, bApply ? TEXT("true") : TEXT("false"), bRollback ? TEXT("true") : TEXT("false"), bAllowPublicFixtureWrite ? TEXT("true") : TEXT("false"));

    TSharedPtr<FJsonObject> Output = MakeShared<FJsonObject>();
    Output->SetStringField(TEXT("schema"), TEXT("ai-tool-ta-anim-notify-diagnostics@0.1.0"));
    Output->SetStringField(TEXT("input"), InputPath);
    Output->SetStringField(TEXT("singleAnimPath"), SingleAnimPath);
    Output->SetBoolField(TEXT("apply"), bApply);
    Output->SetBoolField(TEXT("rollback"), bRollback);
    Output->SetBoolField(TEXT("allowPublicFixtureWrite"), bAllowPublicFixtureWrite);
    Output->SetNumberField(TEXT("assetWrites"), 0);
    Output->SetNumberField(TEXT("engineWrites"), 0);
    Output->SetNumberField(TEXT("productionWrites"), 0);

    TArray<FString> AssetPaths;
    AddUniqueString(AssetPaths, SingleAnimPath);

    TSharedPtr<FJsonObject> InputObject;
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

        TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(InputText);
        if (!FJsonSerializer::Deserialize(Reader, InputObject) || !InputObject.IsValid())
        {
            Output->SetStringField(TEXT("status"), TEXT("blocked_by_invalid_input_json"));
            Output->SetStringField(TEXT("message"), TEXT("Input report is not valid JSON."));
            WriteOutput(OutputPath, Output);
            UE_LOG(LogTemp, Error, TEXT("Input report is not valid JSON: %s"), *InputPath);
            return 4;
        }

        const TArray<TSharedPtr<FJsonValue>>* RequestValues = nullptr;
        if (bApply || InputObject->TryGetArrayField(TEXT("requests"), RequestValues))
        {
            return RunAuthoringMode(InputObject, InputPath, OutputPath, bApply, bRollback, bAllowPublicFixtureWrite);
        }
        CollectAssetPathsFromJsonObject(InputObject, AssetPaths);
    }
    else if (bApply)
    {
        Output->SetStringField(TEXT("status"), TEXT("blocked_by_missing_input_report"));
        Output->SetStringField(TEXT("message"), TEXT("Apply mode requires an Input receipt."));
        WriteOutput(OutputPath, Output);
        UE_LOG(LogTemp, Error, TEXT("Apply mode requires an Input receipt."));
        return 3;
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
