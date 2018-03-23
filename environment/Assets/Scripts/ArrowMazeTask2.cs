using UnityEngine;

public class ArrowMazeTask2 : Task {
	int waitedTime = 0;
	bool waited = false;

	public override string Name() { return "Arrow Maze Task 2"; }

	public override void Initialize(int success, int failure) {
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

	void Update() {
		float x = agent.transform.position.x;

		if(0.0f <= x && x <= 4.0f) {
			if(!waited && (waitedTime >= 2 * 60)) {
				Reward.Add(2.0F);
				waited = true;
			}
			waitedTime += 1;
		} else {
			waitedTime = 0;
		}
	}
}
