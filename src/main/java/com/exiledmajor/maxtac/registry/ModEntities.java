package com.exiledmajor.maxtac.registry;

import com.exiledmajor.maxtac.MaxtacDevelopment;
import com.exiledmajor.maxtac.entity.WardenAvEntity;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.function.Supplier;

public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITY_TYPES =
            DeferredRegister.create(Registries.ENTITY_TYPE, MaxtacDevelopment.MOD_ID);

    public static final Supplier<EntityType<WardenAvEntity>> WARDEN_AV = ENTITY_TYPES.register(
            "warden_av",
            () -> EntityType.Builder.<WardenAvEntity>of(WardenAvEntity::new, MobCategory.MISC)
                    .sized(6.375F, 2.35F)
                    .clientTrackingRange(12)
                    .updateInterval(1)
                    .build("warden_av")
    );

    private ModEntities() {}

    public static void register(IEventBus modEventBus) {
        ENTITY_TYPES.register(modEventBus);
    }
}
