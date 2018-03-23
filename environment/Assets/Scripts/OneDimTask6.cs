using UnityEngine;

public class OneDimTask6 : Task {
    public GameObject reward;

    bool rewardShown = false;
    int waited = 0;

    Range range;

    public override string Name() { return "One Dimensional Task 6"; }

    public override void Initialize(int success, int failure) {
        switch((success + failure) % 3) {
        case 0:
            range = Range.Red;
            break;
        case 1:
            range = Range.Green;
            break;
        case 2:
            range = Range.Blue;
            break;
        default:
            break;
        }
    }

    public override bool Success() {
        return rewardCount > 1;
    }

    public override bool Failure() {
        return Reward.Get() < -1.8F;
    }

    public override bool Done(int success, int failure) {
        return (success - failure) > 21;
    }

    void Update() {
        float z = agent.transform.position.z;

        if(range.start <= z && z <= range.end) {
            if(!rewardShown && waited >= 2 * 60) {
                rewardCount += 1;
                Reward.Add(2.0F);

                GameObject rewardObj = (GameObject)GameObject.Instantiate(
                    reward, new Vector3(0.0F, 0.5F, 23.0F), Quaternion.identity
                );

                rewardObj.transform.parent = transform;
                rewardShown = true;
            }

            waited += 1;
        } else {
            waited = 0;
        }
    }
}
