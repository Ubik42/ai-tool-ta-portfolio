#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "AiToolTaSocketBridgeLibrary.generated.h"

class USkeleton;

USTRUCT(BlueprintType)
struct FAiToolTaSocketBridgeRequest
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Tool TA|Socket Bridge")
    FName SocketName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Tool TA|Socket Bridge")
    FName BoneName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Tool TA|Socket Bridge")
    FVector RelativeLocation = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Tool TA|Socket Bridge")
    FRotator RelativeRotation = FRotator::ZeroRotator;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Tool TA|Socket Bridge")
    FVector RelativeScale = FVector::OneVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI Tool TA|Socket Bridge")
    FString SourceReceiptId;
};

USTRUCT(BlueprintType)
struct FAiToolTaSocketBridgeResult
{
    GENERATED_BODY()

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Socket Bridge")
    FName SocketName;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Socket Bridge")
    FName BoneName;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Socket Bridge")
    bool bApplied = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Socket Bridge")
    bool bAlreadyPresent = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Socket Bridge")
    FString Message;
};

UCLASS()
class AI_TOOL_TA_SOCKETBRIDGE_API UAiToolTaSocketBridgeLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "AI Tool TA|Socket Bridge")
    static bool ApplySocketsToSkeleton(
        USkeleton* TargetSkeleton,
        const TArray<FAiToolTaSocketBridgeRequest>& Requests,
        bool bDryRun,
        TArray<FAiToolTaSocketBridgeResult>& Results);
};
