#include "AiToolTaSocketAuthoringCommandlet.h"

#include "AiToolTaSocketBridgeLibrary.h"
#include "Animation/Skeleton.h"
#include "Dom/JsonObject.h"
#include "Misc/FileHelper.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

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
    FParse::Value(*Params, TEXT("Input="), InputPath);
    FParse::Value(*Params, TEXT("Output="), OutputPath);

    UE_LOG(LogTemp, Display, TEXT("AI Tool TA Socket Authoring Commandlet contract loaded."));
    UE_LOG(LogTemp, Display, TEXT("Input=%s Output=%s Apply=%s"), *InputPath, *OutputPath, bApply ? TEXT("true") : TEXT("false"));

    if (InputPath.IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("No Input receipt path supplied; readiness invocation only."));
        return 0;
    }

    TSharedPtr<FJsonObject> Output = MakeShared<FJsonObject>();
    Output->SetStringField(TEXT("schema"), TEXT("ai-tool-ta-socket-commandlet-result@0.1.0"));
    Output->SetStringField(TEXT("input"), InputPath);
    Output->SetBoolField(TEXT("apply"), bApply);
    Output->SetNumberField(TEXT("assetWrites"), 0);
    Output->SetNumberField(TEXT("engineWrites"), 0);
    Output->SetNumberField(TEXT("productionWrites"), 0);

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

    if (bApply)
    {
        Output->SetStringField(TEXT("status"), TEXT("blocked_by_apply_not_enabled"));
        Output->SetStringField(TEXT("message"), TEXT("Apply mode is intentionally disabled until rollback receipt writing is validated."));
        WriteOutput(OutputPath, Output);
        UE_LOG(LogTemp, Warning, TEXT("Apply mode is intentionally disabled until rollback receipt writing is validated."));
        return 2;
    }

    TArray<FAiToolTaSocketBridgeResult> Results;
    const bool bAllAppliedOrPresent = UAiToolTaSocketBridgeLibrary::ApplySocketsToSkeleton(TargetSkeleton, Requests, true, Results);
    TArray<TSharedPtr<FJsonValue>> ResultValues;
    int32 AlreadyPresent = 0;
    int32 WouldCreate = 0;
    for (const FAiToolTaSocketBridgeResult& Result : Results)
    {
        if (Result.bAlreadyPresent)
        {
            AlreadyPresent++;
        }
        if (Result.Message.Contains(TEXT("would be created")))
        {
            WouldCreate++;
        }
        ResultValues.Add(MakeShared<FJsonValueObject>(ResultToJson(Result)));
    }

    Output->SetStringField(TEXT("status"), TEXT("dry_run_completed"));
    Output->SetBoolField(TEXT("dryRun"), true);
    Output->SetBoolField(TEXT("allAppliedOrPresent"), bAllAppliedOrPresent);
    Output->SetNumberField(TEXT("resultCount"), Results.Num());
    Output->SetNumberField(TEXT("alreadyPresent"), AlreadyPresent);
    Output->SetNumberField(TEXT("wouldCreate"), WouldCreate);
    Output->SetArrayField(TEXT("results"), ResultValues);
    if (!WriteOutput(OutputPath, Output))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to write commandlet output: %s"), *OutputPath);
        return 8;
    }
    UE_LOG(LogTemp, Display, TEXT("Dry-run receipt parsed. target=%s requests=%d wouldCreate=%d alreadyPresent=%d"), *TargetSkeletonPath, Requests.Num(), WouldCreate, AlreadyPresent);
    return 0;
}
