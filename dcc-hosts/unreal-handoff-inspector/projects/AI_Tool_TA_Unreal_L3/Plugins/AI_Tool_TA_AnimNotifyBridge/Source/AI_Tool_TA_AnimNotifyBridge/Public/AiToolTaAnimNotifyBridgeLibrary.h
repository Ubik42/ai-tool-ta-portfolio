#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "AiToolTaAnimNotifyBridgeLibrary.generated.h"

class UAnimSequence;

USTRUCT(BlueprintType)
struct FAiToolTaAnimNotifyDiagnosticRow
{
    GENERATED_BODY()

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Anim Notify Bridge")
    FString AnimSequencePath;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Anim Notify Bridge")
    FName NotifyName;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Anim Notify Bridge")
    FString NotifyClass;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Anim Notify Bridge")
    FString NotifyStateClass;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Anim Notify Bridge")
    float TriggerTime = 0.0f;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Anim Notify Bridge")
    float EndTriggerTime = 0.0f;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Anim Notify Bridge")
    float Duration = 0.0f;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Anim Notify Bridge")
    int32 TrackIndex = 0;
};

UCLASS()
class AI_TOOL_TA_ANIMNOTIFYBRIDGE_API UAiToolTaAnimNotifyBridgeLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "AI Tool TA|Anim Notify Bridge")
    static bool CollectAnimNotifyDiagnostics(
        UAnimSequence* AnimSequence,
        TArray<FAiToolTaAnimNotifyDiagnosticRow>& Rows,
        FString& Message);
};
