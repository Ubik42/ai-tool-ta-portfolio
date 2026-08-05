#include "AiToolTaSocketAuthoringCommandlet.h"

#include "AiToolTaSocketBridgeLibrary.h"
#include "Animation/Skeleton.h"
#include "Dom/JsonObject.h"
#include "Engine/SkeletalMeshSocket.h"
#include "Misc/FileHelper.h"
#include "Misc/CommandLine.h"
#include "Misc/PackageName.h"
#include "Misc/Parse.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "UObject/Package.h"
#include "UObject/SavePackage.h"

namespace
{
bool ReadVector(const TSharedPtr<FJsonObject>& Object, const TCHAR* FieldName, FVector& OutValue)
{
    const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
    if (!Object.IsValid() || !Object->TryGetArrayField(FieldName, Values) || !Values || Values->Num() != 3)
    {
        return false;
    }
    OutValue = FVector((*Values)[0]->AsNumber(), (*Values)[1]->AsNumber(), (*Values)[2]->AsNumber());
    return true;
}

bool ReadRotator(const TSharedPtr<FJsonObject>& Object, const TCHAR* FieldName, FRotator& OutValue)
{
    const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
    if (!Object.IsValid() || !Object->TryGetArrayField(FieldName, Values) || !Values || Values->Num() != 3)
    {
        return false;
    }
    OutValue = FRotator((*Values)[0]->AsNumber(), (*Values)[1]->AsNumber(), (*Values)[2]->AsNumber());
    return true;
}

TSharedPtr<FJsonObject> ResultToJson(const FAiToolTaSocketBridgeResult& Result)
{
    TSharedPtr<FJsonObject> Object = MakeShared<FJsonObject>();
    Object->SetStringField(TEXT("socketName"), Result.SocketName.ToString());
    Object->SetStringField(TEXT("boneName"), Result.BoneName.ToString());
    Object->SetBoolField(TEXT("applied"), Result.bApplied);
    Object->SetBoolField(TEXT("alreadyPresent"), Result.bAlreadyPresent);
    Object->SetStringField(TEXT("message"), Result.Message);
    return Object;
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

bool SaveSkeletonPackage(USkeleton* TargetSkeleton, FString& OutPackageFilename)
{
    if (!TargetSkeleton)
    {
        return false;
    }
    UPackage* Package = TargetSkeleton->GetOutermost();
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
    return UPackage::SavePackage(Package, TargetSkeleton, *OutPackageFilename, SaveArgs);
}

int32 CountRequestedSockets(USkeleton* TargetSkeleton, const TArray<FAiToolTaSocketBridgeRequest>& Requests)
{
    if (!TargetSkeleton)
    {
        return 0;
    }
    int32 Count = 0;
    for (const FAiToolTaSocketBridgeRequest& Request : Requests)
    {
        if (TargetSkeleton->FindSocket(Request.SocketName))
        {
            Count++;
        }
    }
    return Count;
}

int32 RemoveCreatedSockets(USkeleton* TargetSkeleton, const TArray<FAiToolTaSocketBridgeRequest>& Requests)
{
    if (!TargetSkeleton)
    {
        return 0;
    }
    int32 Removed = 0;
    for (const FAiToolTaSocketBridgeRequest& Request : Requests)
    {
        for (int32 Index = TargetSkeleton->Sockets.Num() - 1; Index >= 0; --Index)
        {
            USkeletalMeshSocket* Socket = TargetSkeleton->Sockets[Index];
            if (Socket && Socket->SocketName == Request.SocketName && Socket->BoneName == Request.BoneName)
            {
                TargetSkeleton->Sockets.RemoveAt(Index);
                Removed++;
                break;
            }
        }
    }
    if (Removed > 0)
    {
        TargetSkeleton->MarkPackageDirty();
    }
    return Removed;
}
}

UAiToolTaSocketAuthoringCommandlet::UAiToolTaSocketAuthoringCommandlet()
{
    IsClient = false;
    IsEditor = true;
    IsServer = false;
    LogToConsole = true;
}

int32 UAiToolTaSocketAuthoringCommandlet::Main(const FString& Params)
{
    FString InputPath;
    FString OutputPath;
    const bool bApply = FParse::Param(*Params, TEXT("Apply"));
    const bool bRollback = FParse::Param(*Params, TEXT("Rollback"));
    const bool bAllowPublicFixtureWrite = FParse::Param(*Params, TEXT("AllowPublicFixtureWrite"));
    FParse::Value(*Params, TEXT("Input="), InputPath);
    FParse::Value(*Params, TEXT("Output="), OutputPath);

    UE_LOG(LogTemp, Display, TEXT("AI Tool TA Socket Authoring Commandlet contract loaded."));
    UE_LOG(LogTemp, Display, TEXT("Input=%s Output=%s Apply=%s Rollback=%s AllowPublicFixtureWrite=%s"), *InputPath, *OutputPath, bApply ? TEXT("true") : TEXT("false"), bRollback ? TEXT("true") : TEXT("false"), bAllowPublicFixtureWrite ? TEXT("true") : TEXT("false"));

    if (InputPath.IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("No Input receipt path supplied; readiness invocation only."));
        return 0;
    }

    TSharedPtr<FJsonObject> Output = MakeShared<FJsonObject>();
    Output->SetStringField(TEXT("schema"), TEXT("ai-tool-ta-socket-commandlet-result@0.1.0"));
    Output->SetStringField(TEXT("input"), InputPath);
    Output->SetBoolField(TEXT("apply"), bApply);
    Output->SetBoolField(TEXT("rollback"), bRollback);
    Output->SetBoolField(TEXT("allowPublicFixtureWrite"), bAllowPublicFixtureWrite);
    Output->SetNumberField(TEXT("assetWrites"), 0);
    Output->SetNumberField(TEXT("engineWrites"), 0);
    Output->SetNumberField(TEXT("productionWrites"), 0);
    Output->SetNumberField(TEXT("inMemoryWrites"), 0);

    FString InputText;
    if (!FFileHelper::LoadFileToString(InputText, *InputPath))
    {
        Output->SetStringField(TEXT("status"), TEXT("blocked_by_missing_input_receipt"));
        Output->SetStringField(TEXT("message"), TEXT("Input receipt could not be read."));
        WriteOutput(OutputPath, Output);
        UE_LOG(LogTemp, Error, TEXT("Input receipt could not be read: %s"), *InputPath);
        return 3;
    }

    TSharedPtr<FJsonObject> Receipt;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(InputText);
    if (!FJsonSerializer::Deserialize(Reader, Receipt) || !Receipt.IsValid())
    {
        Output->SetStringField(TEXT("status"), TEXT("blocked_by_invalid_input_receipt_json"));
        Output->SetStringField(TEXT("message"), TEXT("Input receipt is not valid JSON."));
        WriteOutput(OutputPath, Output);
        UE_LOG(LogTemp, Error, TEXT("Input receipt is not valid JSON: %s"), *InputPath);
        return 4;
    }

    const FString TargetSkeletonPath = Receipt->GetStringField(TEXT("targetSkeleton"));
    Output->SetStringField(TEXT("targetSkeleton"), TargetSkeletonPath);
    const bool bPublicFixtureTarget = TargetSkeletonPath.StartsWith(TEXT("/Game/AI_Tool_TA/"));
    Output->SetBoolField(TEXT("publicFixtureTarget"), bPublicFixtureTarget);
    USkeleton* TargetSkeleton = LoadObject<USkeleton>(nullptr, *TargetSkeletonPath);
    Output->SetBoolField(TEXT("targetLoaded"), TargetSkeleton != nullptr);
    if (!TargetSkeleton)
    {
        Output->SetStringField(TEXT("status"), TEXT("blocked_by_missing_target_skeleton"));
        Output->SetStringField(TEXT("message"), TEXT("Target Skeleton could not be loaded."));
        WriteOutput(OutputPath, Output);
        UE_LOG(LogTemp, Error, TEXT("Target Skeleton could not be loaded: %s"), *TargetSkeletonPath);
        return 5;
    }

    const TArray<TSharedPtr<FJsonValue>>* RequestValues = nullptr;
    if (!Receipt->TryGetArrayField(TEXT("requests"), RequestValues) || !RequestValues)
    {
        Output->SetStringField(TEXT("status"), TEXT("blocked_by_missing_requests"));
        Output->SetStringField(TEXT("message"), TEXT("Receipt has no requests array."));
        WriteOutput(OutputPath, Output);
        UE_LOG(LogTemp, Error, TEXT("Receipt has no requests array: %s"), *InputPath);
        return 6;
    }

    TArray<FAiToolTaSocketBridgeRequest> Requests;
    for (const TSharedPtr<FJsonValue>& Value : *RequestValues)
    {
        TSharedPtr<FJsonObject> RequestObject = Value.IsValid() ? Value->AsObject() : nullptr;
        if (!RequestObject.IsValid())
        {
            continue;
        }
        FAiToolTaSocketBridgeRequest Request;
        Request.SocketName = FName(*RequestObject->GetStringField(TEXT("socketName")));
        Request.BoneName = FName(*RequestObject->GetStringField(TEXT("boneName")));
        ReadVector(RequestObject, TEXT("relativeLocation"), Request.RelativeLocation);
        ReadRotator(RequestObject, TEXT("relativeRotation"), Request.RelativeRotation);
        ReadVector(RequestObject, TEXT("relativeScale"), Request.RelativeScale);
        Request.SourceReceiptId = RequestObject->GetStringField(TEXT("sourceReceiptId"));
        Requests.Add(Request);
    }

    Output->SetNumberField(TEXT("requestCount"), Requests.Num());
    if (Requests.IsEmpty())
    {
        Output->SetStringField(TEXT("status"), TEXT("blocked_by_empty_requests"));
        Output->SetStringField(TEXT("message"), TEXT("No valid socket requests were parsed."));
        WriteOutput(OutputPath, Output);
        UE_LOG(LogTemp, Error, TEXT("No valid socket requests were parsed: %s"), *InputPath);
        return 7;
    }

    if (bApply && !bAllowPublicFixtureWrite)
    {
        Output->SetStringField(TEXT("status"), TEXT("blocked_by_missing_public_fixture_write_guard"));
        Output->SetStringField(TEXT("message"), TEXT("Apply mode requires -AllowPublicFixtureWrite."));
        WriteOutput(OutputPath, Output);
        UE_LOG(LogTemp, Warning, TEXT("Apply mode requires -AllowPublicFixtureWrite."));
        return 2;
    }
    if (bApply && !bPublicFixtureTarget)
    {
        Output->SetStringField(TEXT("status"), TEXT("blocked_by_non_public_fixture_target"));
        Output->SetStringField(TEXT("message"), TEXT("Apply mode is limited to /Game/AI_Tool_TA public fixture assets."));
        WriteOutput(OutputPath, Output);
        UE_LOG(LogTemp, Warning, TEXT("Apply mode is limited to /Game/AI_Tool_TA public fixture assets: %s"), *TargetSkeletonPath);
        return 9;
    }
    if (bApply && !bRollback)
    {
        Output->SetStringField(TEXT("status"), TEXT("blocked_by_missing_rollback_guard"));
        Output->SetStringField(TEXT("message"), TEXT("Public portfolio execution requires -Rollback so no persistent mutation remains."));
        WriteOutput(OutputPath, Output);
        UE_LOG(LogTemp, Warning, TEXT("Public portfolio execution requires -Rollback."));
        return 10;
    }

    TArray<FAiToolTaSocketBridgeResult> Results;
    const bool bAllAppliedOrPresent = UAiToolTaSocketBridgeLibrary::ApplySocketsToSkeleton(TargetSkeleton, Requests, !bApply, Results);
    TArray<TSharedPtr<FJsonValue>> ResultValues;
    TArray<FAiToolTaSocketBridgeRequest> RollbackRequests;
    int32 AlreadyPresent = 0;
    int32 WouldCreate = 0;
    int32 Applied = 0;
    for (int32 ResultIndex = 0; ResultIndex < Results.Num(); ++ResultIndex)
    {
        const FAiToolTaSocketBridgeResult& Result = Results[ResultIndex];
        if (Result.bAlreadyPresent)
        {
            AlreadyPresent++;
        }
        if (Result.Message.Contains(TEXT("would be created")))
        {
            WouldCreate++;
        }
        if (Result.bApplied)
        {
            Applied++;
            if (Requests.IsValidIndex(ResultIndex))
            {
                RollbackRequests.Add(Requests[ResultIndex]);
            }
        }
        ResultValues.Add(MakeShared<FJsonValueObject>(ResultToJson(Result)));
    }

    Output->SetBoolField(TEXT("dryRun"), !bApply);
    Output->SetBoolField(TEXT("allAppliedOrPresent"), bAllAppliedOrPresent);
    Output->SetNumberField(TEXT("resultCount"), Results.Num());
    Output->SetNumberField(TEXT("alreadyPresent"), AlreadyPresent);
    Output->SetNumberField(TEXT("wouldCreate"), WouldCreate);
    Output->SetNumberField(TEXT("applied"), Applied);
    Output->SetArrayField(TEXT("results"), ResultValues);
    if (!bApply)
    {
        Output->SetStringField(TEXT("status"), TEXT("dry_run_completed"));
        if (!WriteOutput(OutputPath, Output))
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to write commandlet output: %s"), *OutputPath);
            return 8;
        }
        UE_LOG(LogTemp, Display, TEXT("Dry-run receipt parsed. target=%s requests=%d wouldCreate=%d alreadyPresent=%d"), *TargetSkeletonPath, Requests.Num(), WouldCreate, AlreadyPresent);
        return 0;
    }

    Output->SetNumberField(TEXT("inMemoryWrites"), Applied);
    const int32 PostCheckPresent = CountRequestedSockets(TargetSkeleton, Requests);
    Output->SetNumberField(TEXT("postCheckPresent"), PostCheckPresent);
    FString PackageFilename;
    const bool bSavedAfterApply = SaveSkeletonPackage(TargetSkeleton, PackageFilename);
    Output->SetStringField(TEXT("packageFilename"), PackageFilename);
    Output->SetBoolField(TEXT("savedAfterApply"), bSavedAfterApply);
    Output->SetNumberField(TEXT("assetWrites"), bSavedAfterApply ? 1 : 0);
    if (!bSavedAfterApply)
    {
        Output->SetStringField(TEXT("status"), TEXT("blocked_by_apply_save_failure"));
        WriteOutput(OutputPath, Output);
        UE_LOG(LogTemp, Error, TEXT("Failed to save Skeleton package after apply: %s"), *TargetSkeletonPath);
        return 11;
    }

    const int32 RollbackRemoved = RemoveCreatedSockets(TargetSkeleton, RollbackRequests);
    const int32 PostRollbackPresent = CountRequestedSockets(TargetSkeleton, RollbackRequests);
    const bool bSavedAfterRollback = SaveSkeletonPackage(TargetSkeleton, PackageFilename);
    Output->SetNumberField(TEXT("rollbackRemoved"), RollbackRemoved);
    Output->SetNumberField(TEXT("postRollbackPresent"), PostRollbackPresent);
    Output->SetBoolField(TEXT("savedAfterRollback"), bSavedAfterRollback);
    Output->SetNumberField(TEXT("assetWrites"), (bSavedAfterApply ? 1 : 0) + (bSavedAfterRollback ? 1 : 0));
    Output->SetBoolField(TEXT("persistentMutation"), PostRollbackPresent != 0);
    const bool bRollbackOk = bSavedAfterRollback && PostRollbackPresent == 0 && RollbackRemoved >= Applied;
    Output->SetStringField(TEXT("status"), bRollbackOk ? TEXT("apply_postcheck_rollback_completed") : TEXT("apply_postcheck_rollback_incomplete"));
    if (!WriteOutput(OutputPath, Output))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to write commandlet output: %s"), *OutputPath);
        return 8;
    }
    UE_LOG(LogTemp, Display, TEXT("Apply/post-check/rollback completed. target=%s applied=%d postCheckPresent=%d rollbackRemoved=%d postRollbackPresent=%d"), *TargetSkeletonPath, Applied, PostCheckPresent, RollbackRemoved, PostRollbackPresent);
    return bRollbackOk ? 0 : 12;
}
