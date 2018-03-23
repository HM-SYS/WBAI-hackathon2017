using UnityEngine;

public class Scenes {
    public static void Init() {
        PlayerPrefs.SetInt("Scene Number", 0);
    }

    public static string First() {
        return PlayerPrefs.GetString("Scene0");
    }

    public static string Next() {
        int nextSceneNumber = PlayerPrefs.GetInt("Scene Number") + 1;

        if(!PlayerPrefs.HasKey("Scene" + nextSceneNumber)) {
            nextSceneNumber = 0;
        }

        PlayerPrefs.SetInt("Scene Number", nextSceneNumber);

        return Get(nextSceneNumber);
    }

    public static string Get(int i) {
        return PlayerPrefs.GetString("Scene" + i);
    }

    public static void Set(int i, string value) {
        PlayerPrefs.SetString("Scene" + i, value);
    }
}
