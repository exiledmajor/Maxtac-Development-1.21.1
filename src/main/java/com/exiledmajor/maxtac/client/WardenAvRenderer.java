package com.exiledmajor.maxtac.client;

import com.exiledmajor.maxtac.entity.WardenAvEntity;
import com.google.gson.*;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

public final class WardenAvRenderer extends EntityRenderer<WardenAvEntity> {
    private static final ResourceLocation MESH = ResourceLocation.fromNamespaceAndPath("maxtac_development", "warden_av_v11.mesh.json");
    private static final ResourceLocation TEXTURE = ResourceLocation.fromNamespaceAndPath("maxtac_development", "warden_v11_texture.png");
    // Immutable packed vertices: XYZ, UV, normal XYZ. Parsed once, not every frame.
    private static volatile float[] vertices;

    public WardenAvRenderer(EntityRendererProvider.Context context) { super(context); }

    private static float[] mesh() {
        if (vertices != null) return vertices;
        synchronized (WardenAvRenderer.class) {
            if (vertices != null) return vertices;
            try (var in = Minecraft.getInstance().getResourceManager().open(MESH);
                 var reader = new InputStreamReader(in, StandardCharsets.UTF_8)) {
                JsonArray triangles = JsonParser.parseReader(reader).getAsJsonObject().getAsJsonArray("triangles");
                ArrayList<Float> out = new ArrayList<>(triangles.size() * 24);
                for (JsonElement item : triangles) {
                    JsonObject t=item.getAsJsonObject();
                    JsonArray p=t.getAsJsonArray("positions"), uv=t.getAsJsonArray("uv");
                    JsonArray n=t.has("normal") ? t.getAsJsonArray("normal") : null;
                    float nx,ny,nz;
                    if (n != null) { nx=n.get(0).getAsFloat(); ny=n.get(1).getAsFloat(); nz=n.get(2).getAsFloat(); }
                    else {
                        float ax=p.get(3).getAsFloat()-p.get(0).getAsFloat(), ay=p.get(4).getAsFloat()-p.get(1).getAsFloat(), az=p.get(5).getAsFloat()-p.get(2).getAsFloat();
                        float bx=p.get(6).getAsFloat()-p.get(0).getAsFloat(), by=p.get(7).getAsFloat()-p.get(1).getAsFloat(), bz=p.get(8).getAsFloat()-p.get(2).getAsFloat();
                        nx=ay*bz-az*by; ny=az*bx-ax*bz; nz=ax*by-ay*bx;
                        float len=(float)Math.sqrt(nx*nx+ny*ny+nz*nz);
                        if (len>1.0e-6F) { nx/=len; ny/=len; nz/=len; }
                    }
                    for(int i=0;i<3;i++) {
                        out.add(p.get(i*3).getAsFloat()); out.add(p.get(i*3+1).getAsFloat()); out.add(p.get(i*3+2).getAsFloat());
                        out.add(uv.get(i*2).getAsFloat()/512.0F); out.add(uv.get(i*2+1).getAsFloat()/512.0F);
                        out.add(nx); out.add(ny); out.add(nz);
                    }
                }
                float[] packed=new float[out.size()];
                for(int i=0;i<packed.length;i++) packed[i]=out.get(i);
                vertices=packed;
                return packed;
            } catch(Exception e) { throw new IllegalStateException("Unable to load Warden AV mesh",e); }
        }
    }

    @Override
    public void render(WardenAvEntity entity, float yaw, float partialTick, PoseStack stack, MultiBufferSource buffers, int light) {
        float[] data=mesh();
        stack.pushPose();
        stack.translate(0.0D,-1.175D,0.0D);
        stack.mulPose(com.mojang.math.Axis.YP.rotationDegrees(180.0F-yaw));
        stack.scale(0.0625F,0.0625F,0.0625F);
        PoseStack.Pose pose=stack.last();
        VertexConsumer consumer=buffers.getBuffer(RenderType.entityCutoutNoCull(TEXTURE));
        for(int i=0;i<data.length;i+=8) {
            consumer.addVertex(pose,data[i],data[i+1],data[i+2])
                .setColor(255,255,255,255).setUv(data[i+3],data[i+4])
                .setOverlay(0).setLight(light).setNormal(pose,data[i+5],data[i+6],data[i+7]);
        }
        stack.popPose();
        super.render(entity,yaw,partialTick,stack,buffers,light);
    }

    @Override public ResourceLocation getTextureLocation(WardenAvEntity entity) { return TEXTURE; }
}
