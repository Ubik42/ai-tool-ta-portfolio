#pragma once

#include "Commandlets/Commandlet.h"
#include "AiToolTaControlRigDiagnosticsCommandlet.generated.h"

UCLASS()
class AI_TOOL_TA_CONTROLRIGBRIDGE_API UAiToolTaControlRigDiagnosticsCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    UAiToolTaControlRigDiagnosticsCommandlet();
    virtual int32 Main(const FString& Params) override;
};
