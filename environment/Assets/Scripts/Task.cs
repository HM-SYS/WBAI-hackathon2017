using UnityEngine;

public abstract class Task : MonoBehaviour {
    public Agent agent;

    protected int rewardCount = 0;

    public abstract string Name();

    public virtual void Initialize(int success, int failure) {
        return;
    }

    public abstract bool Success();
    public abstract bool Failure();
    public abstract bool Done(int success, int failure);

    public virtual void Reset() {
        agent.behaviour.Reset();
    }

    public virtual void Finish() {
        agent.behaviour.Finish();
    }

    protected virtual void OnRewardCollision() {
        rewardCount += 1;
        Reward.Add(2.0F);
    }

    protected virtual void Punishment() {
        Reward.Add(-0.001F);
    }

    void Start() {
        NotificationCenter.DefaultCenter.AddObserver(this, "OnRewardCollision");
    }

    void FixedUpdate() {
        Punishment();
    }
}
