using UnityEngine;

public class CrossMazeTask1 : Task {
	public override string Name() { return "Cross Maze Task 1"; }

	public override void Initialize(int success, int failure) {
		// 仕様「S地点は3ヶ所あり、ランダムにスタート地点が決定する」を実現する

		int phase = (int)(Random.value * 3);
		float x = 0.0f;
		float y = 1.12f;
		float z = 0.5f;

		float rx = 0.0f;
		float ry = 0.0f;
		float rz = 0.0f;
		Quaternion rotation = Quaternion.identity;
			
		switch(phase) {
		case 0:
			// 南端からスタート {0, 0, 0}
			break;
		case 1:
			// 東端からスタート {0, 0, 0}
			x = 12.0f;
			z = 12.5f;
			ry = -90.0f;
			break;
		case 2:
			// 西端からスタート {0, 0, 0}
			x = -12.0f;
			z = 12.5f;
			ry = 90.0f;
			break;
		default:
			break;
		}

		agent.transform.position = new Vector3(x, y, z);
		rotation.eulerAngles = new Vector3 (rx, ry, rz);
		agent.transform.rotation = rotation;
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
