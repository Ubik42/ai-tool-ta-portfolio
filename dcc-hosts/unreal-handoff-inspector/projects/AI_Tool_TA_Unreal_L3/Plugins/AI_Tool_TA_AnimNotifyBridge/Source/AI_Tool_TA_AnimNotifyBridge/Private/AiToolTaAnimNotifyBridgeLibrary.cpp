#include "AiToolTaAnimNotifyBridgeLibrary.h"

#include "Animation/AnimNotifies/AnimNotify.h"
#include "Animation/AnimNotifies/AnimNotifyState.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimTypes.h"

bool UAiToolTaAnimNotifyBridgeLibrary::CollectAnimNotifyDiagnostics(
    UAnimSequence* AnimSequence,
    TArray<FAiToolTaAnimNotifyDiagnosticRow>& Rows,
    FString& Message)
{
    Rows.Reset();

    if (!AnimSequence)
    {
        Message = TEXT("Missing AnimSequence.");
        return false;
    }

    for (const FAnimNotifyEvent& Event : AnimSequence->Notifies)
    {
        FAiToolTaAnimNotifyDiagnosticRow Row;
        Row.AnimSequencePath = AnimSequence->GetPathName();
        Row.NotifyName = Event.NotifyName;
        Row.NotifyClass = Event.Notify ? Event.Notify->GetClass()->GetName() : FString();
        Row.NotifyStateClass = Event.NotifyStateClass ? Event.NotifyStateClass->GetClass()->GetName() : FString();
        Row.TriggerTime = Event.GetTriggerTime();
        Row.EndTriggerTime = Event.GetEndTriggerTime();
        Row.Duration = Event.GetDuration();
        Row.TrackIndex = Event.TrackIndex;
        Rows.Add(Row);
    }

    Message = FString::Printf(TEXT("Collected %d notify diagnostics from %s."), Rows.Num(), *AnimSequence->GetPathName());
    return true;
}
