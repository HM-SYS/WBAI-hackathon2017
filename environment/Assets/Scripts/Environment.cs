using UnityEngine;
using UnityEngine.UI;
using UnityEditor.SceneManagement;

[RequireComponent(typeof (Task))]
public class Environment : MonoBehaviour {
    [SerializeField]
    Text taskText;

    [SerializeField]
    Text successText;

    [SerializeField]
    Text failureText;

    [SerializeField]
    Text rewardText;

    Task task;

    int successCount;
    int failureCount;

    int elapsed = 0;

    void Start() {
        task = GetComponent<Task>();

        Reward.Set(0.0F);

        if(!PlayerPrefs.HasKey("Task Name")) {
            PlayerPrefs.SetString("Task Name", task.Name());
            PlayerPrefs.SetInt("Success Count", 0);
            PlayerPrefs.SetInt("Failure Count", 0);
        }

        if(PlayerPrefs.GetString("Task Name") != task.Name()) {
            PlayerPrefs.SetString("Task Name", task.Name());
            PlayerPrefs.SetInt("Success Count", 0);
            PlayerPrefs.SetInt("Failure Count", 0);
        }

        PlayerPrefs.SetInt("Elapsed Time", elapsed);

        successCount = PlayerPrefs.GetInt("Success Count");
        failureCount = PlayerPrefs.GetInt("Failure Count");

        task.Initialize(successCount, failureCount);

        taskText.text = PlayerPrefs.GetString("Task Name");
        successText.text = "Success: " + successCount;
        failureText.text = "Failure: " + failureCount;
        rewardText.text = "Reward: 0";
    }

    void Update() {
        rewardText.text = "Reward: " + Reward.Get();

        if(task.Success()) {
            task.Reset();

            if(task.Done(successCount, failureCount)) {
                task.Finish();

                PlayerPrefs.SetInt("Success Count", 0);
                PlayerPrefs.SetInt("Failure Count", 0);
                EditorSceneManager.LoadScene(Scenes.Next());
                return;
            }

            PlayerPrefs.SetInt("Success Count", successCount + 1);
            EditorSceneManager.LoadScene(EditorSceneManager.GetActiveScene().name);
            return;
        }

        if(task.Failure()) {
            task.Reset();

            PlayerPrefs.SetInt("Failure Count", failureCount + 1);
            EditorSceneManager.LoadScene(EditorSceneManager.GetActiveScene().name);
            return;
        }

        elapsed += 1;

        PlayerPrefs.SetInt("Elapsed Time", elapsed);
    }
}
