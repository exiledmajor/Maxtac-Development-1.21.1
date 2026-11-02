package com.exiledmajor.maxtac.client;

import com.exiledmajor.maxtac.entity.WardenAvEntity;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import org.joml.Matrix4f;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

public final class WardenAvRenderer extends EntityRenderer<WardenAvEntity> {
    private static final ResourceLocation MESH = ResourceLocation.fromNamespaceAndPath(
            "maxtac_development", "warden_av_v11.mesh.json");
    private static final ResourceLocation TEXTURE = ResourceLocation.fromNamespaceAndPath(
            "maxtac_development", "warden_v11_texture.png");
    private static JsonArray triangles;

    public WardenAvRenderer(EntityRendererProvider.Context context) {
        super(context);
    }

    private static JsonArray getTriangles() {
        if (triangles != null) return triangles;
        try (var stream = Minecraft.getInstance().getResourceManager().open(MESH);
             var reader = new InputStreamReader(stream, StandardCharsets.UTF_8)) {
            JsonObject root = JsonParser.parseReader(reader).getAsJsonObject();
            triangles = root.getAsJsonArray("triangles");
        } catch (Exception exception) {
            throw new IllegalStateException("Unable to load Warden AV mesh asset", exception);
        }
        return triangles;
    }

    @Override
    public void render(WardenAvEntity entity, float entityYaw, float partialTick,
                       PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        JsonArray mesh = getTriangles();
        poseStack.pushPose();
        poseStack.translate(0.0D, -1.175D, 0.0D);
        poseStack.mulPose(com.mojang.math.Axis.YP.rotationDegrees(180.0F - entityYaw));
        poseStack.scale(0.0625F, 0.0625F, 0.0625F);

        PoseStack.Pose pose = poseStack.last();
        Matrix4f positionMatrix = pose.pose();
        VertexConsumer consumer = buffer.getBuffer(RenderType.entityCutout(TEXTURE));

        for (JsonElement element : mesh) {
            JsonObject triangle = element.getAsJsonObject();
            JsonArray p = triangle.getAsJsonArray("positions");
            JsonArray uv = triangle.getAsJsonArray("uv");
            float x0=p.get(0).getAsFloat(), y0=p.get(1).getAsFloat(), z0=p.get(2).getAsFloat();
            float x1=p.get(3).getAsFloat(), y1=p.get(4).getAsFloat(), z1=p.get(5).getAsFloat();
            float x2=p.get(6).getAsFloat(), y2=p.get(7).getAsFloat(), z2=p.get(8).getAsFloat();
            float ax=x1-x0, ay=y1-y0, az=z1-z0, bx=x2-x0, by=y2-y0, bz=z2-z0;
            float nx=ay*bz-az*by, ny=az*bx-ax*bz, nz=ax*by-ay*bx;
            float length=(float)Math.sqrt(nx*nx+ny*ny+nz*nz);
            if (length > 0.00001F) { nx/=length; ny/=length; nz/=length; }
            for (int i=0;i<3;i++) {
                float x=p.get(i*3).getAsFloat(), y=p.get(i*3+1).getAsFloat(), z=p.get(i*3+2).getAsFloat();
                float u=uv.get(i*2).getAsFloat()/512.0F, v=uv.get(i*2+1).getAsFloat()/512.0F;
                consumer.addVertex(positionMatrix, x, y, z)
                        .setColor(255,255,255,255)
                        .setUv(u,v)
                        .setOverlay(0)
                        .setLight(packedLight)
                        .setNormal(pose,nx,ny,nz);
            }
        }
        poseStack.popPose();
        super.render(entity, entityYaw, partialTick, poseStack, buffer, packedLight);
    }

    @Override
    public ResourceLocation getTextureLocation(WardenAvEntity entity) {
        return TEXTURE;
    }
}
