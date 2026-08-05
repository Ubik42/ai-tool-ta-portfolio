#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "AiToolTaSocketAuthoringCommandlet.generated.h"

UCLASS()
class AI_TOOL_TA_SOCKETBRIDGE_API UAiToolTaSocketAuthoringCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    UAiToolTaSocketAuthoringCommandlet();

    virtual int32 Main(const FString& Params) override;
};
