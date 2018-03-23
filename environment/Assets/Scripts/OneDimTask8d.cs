using UnityEngine;

public class OneDimTask8d : Task {
	public GameObject reward;
	public ShapeSelector selector;

	bool rewardShown = false;
	int waited = 0;
	int elapsed = 0;

	Range range;

	public override string Name() { return "One Dimensional Task 8-d"; }

	public override void Initialize(int success, int failure) {
		int phase = (int)(Random.value * 3);

		selector.Selection = phase;

		switch(phase) {
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

		if(elapsed < 120) {
			agent.controller.Paralyzed = true;
			selector.Visible = true;
			elapsed += 1;
		} else {
			agent.controller.Paralyzed = false;
			selector.Visible = false;
		}

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
