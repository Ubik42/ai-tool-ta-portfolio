#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "AiToolTaAnimNotifyDiagnosticsCommandlet.generated.h"

UCLASS()
class AI_TOOL_TA_ANIMNOTIFYBRIDGE_API UAiToolTaAnimNotifyDiagnosticsCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    UAiToolTaAnimNotifyDiagnosticsCommandlet();

    virtual int32 Main(const FString& Params) override;
};
