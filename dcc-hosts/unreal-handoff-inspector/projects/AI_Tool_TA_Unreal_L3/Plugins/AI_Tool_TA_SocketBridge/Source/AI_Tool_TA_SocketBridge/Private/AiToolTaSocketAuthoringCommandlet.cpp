#include "AiToolTaSocketAuthoringCommandlet.h"

#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

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

    if (!bApply)
    {
        UE_LOG(LogTemp, Display, TEXT("Dry-run contract invocation. Use -Apply only for approved public fixture writes."));
        return 0;
    }

    UE_LOG(LogTemp, Warning, TEXT("Apply mode is intentionally unimplemented in the public skeleton until JSON receipt parsing and rollback receipt writing are validated."));
    return 2;
}
