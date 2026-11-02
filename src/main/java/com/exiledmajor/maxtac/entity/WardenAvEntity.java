package com.exiledmajor.maxtac.entity;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;

public final class WardenAvEntity extends Entity {
    // The aircraft model is roughly six blocks across, while the base entity
    // dimensions are intentionally small. Expand only the render-culling box
    // so the model is not clipped when the camera sees its extremities.
    private static final double CULL_HORIZONTAL = 4.0D;
    private static final double CULL_VERTICAL = 2.0D;

    public WardenAvEntity(EntityType<? extends WardenAvEntity> type, Level level) {
        super(type, level);
        this.setNoGravity(true);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
    }

    @Override
    protected void readAdditionalSaveData(CompoundTag tag) {
    }

    @Override
    protected void addAdditionalSaveData(CompoundTag tag) {
    }

    @Override
    public AABB getBoundingBoxForCulling() {
        return this.getBoundingBox().inflate(CULL_HORIZONTAL, CULL_VERTICAL, CULL_HORIZONTAL);
    }

    @Override
    public void tick() {
        super.tick();
        this.setNoGravity(true);
    }
}
