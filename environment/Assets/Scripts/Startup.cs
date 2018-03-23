using UnityEngine;
using UnityEditor.SceneManagement;

public class Startup : MonoBehaviour {
    [SerializeField]
    float RotationSpeed;

    [SerializeField]
    float MovementSpeed;

    [SerializeField]
    string[] SceneNames = {
        "OneDimTask1",
        "OneDimTask2",
        "OneDimTask3",
        "OneDimTask4",
        "OneDimTask5",
        "OneDimTask6",
        "OneDimTask7",

        "CrossMazeTask1",
        "CrossMazeTask2",

        "ArrowMazeTask1",
        "ArrowMazeTask2",
        "ArrowMazeTask3",

		"OneDimTask8a",
		"OneDimTask8b",
		"OneDimTask8c",
		"OneDimTask8d",

	
	};

    [SerializeField]
    bool ManualOverride = false;

    void Start () {
        PlayerPrefs.DeleteAll();
        PlayerPrefs.SetFloat("Rotation Speed", RotationSpeed);
        PlayerPrefs.SetFloat("Movement Speed", MovementSpeed);
        PlayerPrefs.SetInt("Manual Override", ManualOverride ? 1 : 0);

        for(int i = 0; i < SceneNames.Length; ++i) {
            Scenes.Set(i, SceneNames[i]);
        }

        Scenes.Init();

        EditorSceneManager.LoadScene(Scenes.First());
    }
}
