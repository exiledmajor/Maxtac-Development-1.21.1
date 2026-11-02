package com.exiledmajor.maxtac;

import com.exiledmajor.maxtac.registry.ModEntities;
import net.neoforged.fml.common.Mod;

@Mod(MaxtacDevelopment.MOD_ID)
public final class MaxtacDevelopment {
    public static final String MOD_ID = "maxtac_development";

    public MaxtacDevelopment(net.neoforged.bus.api.IEventBus modEventBus) {
        ModEntities.register(modEventBus);
    }
}
