#include "AiToolTaSocketBridgeLibrary.h"

#include "Animation/Skeleton.h"
#include "Engine/SkeletalMeshSocket.h"

namespace
{
FAiToolTaSocketBridgeResult MakeResult(const FAiToolTaSocketBridgeRequest& Request, bool bApplied, bool bAlreadyPresent, const FString& Message)
{
    FAiToolTaSocketBridgeResult Result;
    Result.SocketName = Request.SocketName;
    Result.BoneName = Request.BoneName;
    Result.bApplied = bApplied;
    Result.bAlreadyPresent = bAlreadyPresent;
    Result.Message = Message;
    return Result;
}
}

bool UAiToolTaSocketBridgeLibrary::ApplySocketsToSkeleton(
    USkeleton* TargetSkeleton,
    const TArray<FAiToolTaSocketBridgeRequest>& Requests,
    bool bDryRun,
    TArray<FAiToolTaSocketBridgeResult>& Results)
{
    Results.Reset();

    if (!TargetSkeleton)
    {
        for (const FAiToolTaSocketBridgeRequest& Request : Requests)
        {
            Results.Add(MakeResult(Request, false, false, TEXT("Missing target Skeleton.")));
        }
        return false;
    }

    bool bAllAppliedOrPresent = true;
    for (const FAiToolTaSocketBridgeRequest& Request : Requests)
    {
        if (Request.SocketName.IsNone() || Request.BoneName.IsNone())
        {
            bAllAppliedOrPresent = false;
            Results.Add(MakeResult(Request, false, false, TEXT("SocketName and BoneName are required.")));
            continue;
        }

        if (TargetSkeleton->FindSocket(Request.SocketName))
        {
            Results.Add(MakeResult(Request, false, true, TEXT("Socket already exists on Skeleton.")));
            continue;
        }

        if (bDryRun)
        {
            bAllAppliedOrPresent = false;
            Results.Add(MakeResult(Request, false, false, TEXT("Dry-run: socket would be created.")));
            continue;
        }

        USkeletalMeshSocket* Socket = NewObject<USkeletalMeshSocket>(TargetSkeleton);
        Socket->SocketName = Request.SocketName;
        Socket->BoneName = Request.BoneName;
        Socket->RelativeLocation = Request.RelativeLocation;
        Socket->RelativeRotation = Request.RelativeRotation;
        Socket->RelativeScale = Request.RelativeScale;

        TargetSkeleton->Sockets.Add(Socket);
        TargetSkeleton->MarkPackageDirty();
        Results.Add(MakeResult(Request, true, false, TEXT("Socket created on Skeleton.")));
    }

    return bAllAppliedOrPresent;
}
