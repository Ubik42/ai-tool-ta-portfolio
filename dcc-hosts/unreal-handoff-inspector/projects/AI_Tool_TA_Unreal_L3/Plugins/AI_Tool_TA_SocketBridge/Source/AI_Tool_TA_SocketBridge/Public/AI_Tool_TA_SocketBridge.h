#pragma once

#include "Modules/ModuleManager.h"

class FAI_Tool_TA_SocketBridgeModule final : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
