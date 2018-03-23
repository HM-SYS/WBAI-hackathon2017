using UnityEngine;

class Reward {
    public static float Get() {
        return PlayerPrefs.GetFloat("Reward");
    }

    public static void Set(float value) {
        PlayerPrefs.SetFloat("Reward", value);
    }

    public static void Add(float value) {
        PlayerPrefs.SetFloat("Reward", PlayerPrefs.GetFloat("Reward") + value);
    }
}
