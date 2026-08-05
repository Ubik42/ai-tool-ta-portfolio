using UnrealBuildTool;

public class AI_Tool_TA_SocketBridge : ModuleRules
{
    public AI_Tool_TA_SocketBridge(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(
            new[]
            {
                "Core",
                "CoreUObject",
                "Engine"
            }
        );

        PrivateDependencyModuleNames.AddRange(
            new[]
            {
                "AssetRegistry",
                "Json",
                "JsonUtilities",
                "UnrealEd"
            }
        );
    }
}
