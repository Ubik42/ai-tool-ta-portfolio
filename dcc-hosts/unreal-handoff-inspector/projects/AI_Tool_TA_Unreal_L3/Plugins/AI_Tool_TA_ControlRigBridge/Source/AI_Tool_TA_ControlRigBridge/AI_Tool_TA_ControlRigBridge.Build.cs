using UnrealBuildTool;

public class AI_Tool_TA_ControlRigBridge : ModuleRules
{
    public AI_Tool_TA_ControlRigBridge(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(
            new string[]
            {
                "Core",
                "CoreUObject",
                "Engine"
            }
        );

        PrivateDependencyModuleNames.AddRange(
            new string[]
            {
                "AssetRegistry",
                "Json",
                "JsonUtilities",
                "UnrealEd"
            }
        );
    }
}
