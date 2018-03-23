using UnityEngine;

public class RewardBehaviour : MonoBehaviour {
    void OnCollisionEnter(Collision col) {
        if(col.gameObject.tag == "Player") {
            Destroy(gameObject);
        }
    }
}
