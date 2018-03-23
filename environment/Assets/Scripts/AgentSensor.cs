using UnityEngine;
using System.Collections.Generic;


public class AgentSensor : MonoBehaviour {
    [SerializeField]
    List<Camera> rgbCameras;

    [SerializeField]
    List<Camera> depthCameras;

    private List<Texture2D> rgbTextures;
    private List<Texture2D> depthTextures;


    Texture2D generateTexture(Camera cam) {
        int width = cam.targetTexture.width;
        int height = cam.targetTexture.height;
        return new Texture2D(width, height, TextureFormat.RGB24, false);
    }

    byte[] GetCameraImage(Camera cam, ref Texture2D tex) {
        RenderTexture currentRenderTexture = RenderTexture.active;
        RenderTexture.active = cam.targetTexture;
        cam.Render();
        tex.ReadPixels(new Rect(0, 0, cam.targetTexture.width, cam.targetTexture.height), 0, 0);
        tex.Apply();
        RenderTexture.active = currentRenderTexture;
        return tex.EncodeToPNG();
    }

    byte[][] GetImages(List<Camera> cameras, List<Texture2D> textures) {
        byte[][] images = new byte[cameras.Count][];
        for(int i = 0; i < cameras.Count; ++i) {
            Camera camera = cameras[i];
            Texture2D texture = textures[i];
            images[i] = GetCameraImage(camera, ref texture);
        }
        return images;
    }

    public byte[][] GetRgbImages() {
        return GetImages(rgbCameras, rgbTextures);
    }

    public byte[][] GetDepthImages() {
        return GetImages(depthCameras, depthTextures);
    }

    void Start() {
        rgbTextures = new List<Texture2D>(rgbCameras.Count);
        foreach(var cam in rgbCameras) {
            rgbTextures.Add(generateTexture(cam));
        }

        depthTextures = new List<Texture2D>(depthCameras.Count);
        foreach(var cam in depthCameras) {
            depthTextures.Add(generateTexture(cam));
        }
        
        foreach(var cam in depthCameras) {
            cam.depthTextureMode = DepthTextureMode.Depth;
            cam.SetReplacementShader(Shader.Find("Custom/ReplacementShader"), "");
        }
    }
}
