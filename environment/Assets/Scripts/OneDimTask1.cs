using UnityEngine;

public class OneDimTask1 : Task {
    public override string Name() { return "One Dimensional Task 1"; }

    public override void Initialize(int success, int failure) {
        float z = (float)(22 - (success - failure));
        agent.transform.position = new Vector3(0.0F, 1.12F, z);
    }

    public override bool Success() {
        return rewardCount > 0;
    }

    public override bool Failure() {
        return Reward.Get() < -1.8F;
    }

    public override bool Done(int success, int failure) {
        return (success - failure) > 21;
    }
}
