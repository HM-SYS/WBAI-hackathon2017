using UnityEngine;

public class CrossMazeTask2 : Task {
	public override string Name() { return "Cross Maze Task 2"; }

	public override void Initialize(int success, int failure) {
		// 仕様「S地点は中心で、向きはランダム」を実現する

		int phase = (int)(Random.value * 4);
		float rx = 0.0f;
		float ry = 0.0f;
		float rz = 0.0f;
		Quaternion rotation = Quaternion.identity;

		switch(phase) {
		case 0:
			// 北向きでスタート {0, 0, 0}
			ry = 0.0f;
			break;
		case 1:
			// 西向きでスタート {0, 0, 0}
			ry = -90.0f;
			break;
		case 2:
			// 東向きでスタート {0, 0, 0}
			ry = 90.0f;
			break;
		case 3:
			// 向きでスタート {0, 0, 0}
			ry = 180.0f;
			break;
		default:
			break;
		}

		rotation.eulerAngles = new Vector3 (rx, ry, rz);
		agent.transform.rotation = rotation;
	}

	public override bool Success() {
		return rewardCount > 2;
	}

	public override bool Failure() {
		return Reward.Get() < -1.8F;
	}

	public override bool Done(int success, int failure) {
		return (success - failure) > 21;
	}
}
