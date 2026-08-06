#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "AiToolTaControlRigBridgeLibrary.generated.h"

USTRUCT(BlueprintType)
struct FAiToolTaControlRigDiagnosticRow
{
    GENERATED_BODY()

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Control Rig Bridge")
    FString ControlRigPath;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Control Rig Bridge")
    FString AssetClass;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Control Rig Bridge")
    bool bAssetLoaded = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Control Rig Bridge")
    int32 CompileMethodCount = 0;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Control Rig Bridge")
    int32 DiagnosticMethodCount = 0;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Control Rig Bridge")
    int32 ReadablePropertyCount = 0;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Control Rig Bridge")
    bool bCompileInvoked = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Control Rig Bridge")
    bool bCompileSucceeded = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Control Rig Bridge")
    bool bDirectStatusReadable = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI Tool TA|Control Rig Bridge")
    FString Message;
};

UCLASS()
class AI_TOOL_TA_CONTROLRIGBRIDGE_API UAiToolTaControlRigBridgeLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "AI Tool TA|Control Rig Bridge")
    static bool CollectControlRigDiagnostics(
        UObject* ControlRigBlueprint,
        TArray<FAiToolTaControlRigDiagnosticRow>& Rows,
        FString& Message);
};
