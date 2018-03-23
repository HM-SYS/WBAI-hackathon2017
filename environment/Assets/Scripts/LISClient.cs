using System;
using System.Collections.Generic;
using CI.HttpClient;


public class LISClient {
    private HttpClient client = new HttpClient();
    private Queue<string> queue = new Queue<string>(){};

    public string host = "localhost";
    public string port = "8765";

    public bool HasAction = false;
    public bool Calling = false;

    private Uri createUri;
    private Uri stepUri;
    private Uri resetUri;
    private Uri flushUri;

    public LISClient(string identifier) {
        createUri = new Uri("http://" + host + ":" + port + "/create/" + identifier);
        stepUri   = new Uri("http://" + host + ":" + port + "/step/" + identifier);
        resetUri  = new Uri("http://" + host + ":" + port + "/reset/" + identifier);
        flushUri  = new Uri("http://" + host + ":" + port + "/flush/" + identifier);
    }

    public string GetAction() {
        string action = queue.Dequeue();
        HasAction = (queue.Count > 0);
        return action;
    }

    void Call(Uri uri, byte[] payload) {
        Calling = true;
        client.Post(uri, new ByteArrayContent(payload, "text/plain"), (r) => {
                queue.Enqueue(r.Data);
                HasAction = true;
                Calling = false;
            });
    }

    public void Create(byte[] payload) {
        Call(createUri, payload);
    }
	
    public void Step(byte[] payload) {
        Call(stepUri, payload);
    }

    public void Reset(byte[] payload) {
        Call(resetUri, payload);
    }

    public void Flush(byte[] payload) {
        Call(flushUri, payload);
    }
}
