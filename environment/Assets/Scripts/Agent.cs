using UnityEngine;
using System.Collections;

[RequireComponent(typeof (AgentController))]
[RequireComponent(typeof (AgentSensor))]
[RequireComponent(typeof (AgentBehaviour))]
public class Agent : MonoBehaviour {
    [HideInInspector]
    public AgentController controller;

    [HideInInspector]
    public AgentSensor sensor;

    [HideInInspector]
    public AgentBehaviour behaviour;

    void Start() {
        controller = GetComponent<AgentController>();
        sensor = GetComponent<AgentSensor>();
        behaviour = GetComponent<AgentBehaviour>();
    }
}
