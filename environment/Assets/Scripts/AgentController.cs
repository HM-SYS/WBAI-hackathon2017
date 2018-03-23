using UnityEngine;

[RequireComponent(typeof (CharacterController))]
public class AgentController : MonoBehaviour {
    float rotationSpeed = 10.0F;
    float movementSpeed = 1.0F;

    [HideInInspector]
    public bool Paralyzed = false;

    public void Start() {
        if(!PlayerPrefs.HasKey("Rotation Speed")) {
            PlayerPrefs.SetFloat("RotationSpeed", rotationSpeed);
        }
        if(!PlayerPrefs.HasKey("Movement Speed")) {
            PlayerPrefs.SetFloat("MovementSpeed", movementSpeed);
        }
        rotationSpeed = PlayerPrefs.GetFloat("Rotation Speed");
        movementSpeed = PlayerPrefs.GetFloat("Movement Speed");
    }

    public void PerformAction(string action) {
        CharacterController controller = GetComponent<CharacterController>();

        if(Paralyzed) return;

        bool ManualOverride = PlayerPrefs.GetInt("Manual Override") == 1 ? true : false;

        if(ManualOverride) {
            if(Input.GetKey(KeyCode.RightArrow)) {
                transform.Rotate(Vector3.up, rotationSpeed);
            }

            if(Input.GetKey(KeyCode.LeftArrow)) {
                transform.Rotate(Vector3.down, rotationSpeed);
            }

            if(Input.GetKey(KeyCode.UpArrow)) {
                Vector3 direction = transform.TransformDirection(Vector3.forward * movementSpeed);
                controller.Move(direction);
            }

            return;
        }

        switch(action) {
        case "0":
            transform.Rotate(Vector3.up, rotationSpeed);
            break;
        case "1":
            transform.Rotate(Vector3.down, rotationSpeed);
            break;
        case "2":
            Vector3 direction = transform.TransformDirection(Vector3.forward * movementSpeed);
            controller.Move(direction);
            break;
        default:
            break;
        }
    }
}
