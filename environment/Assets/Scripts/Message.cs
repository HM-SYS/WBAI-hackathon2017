public class Message {
    public float reward = 0.0F;
    public byte[][] image = null;
    public byte[][] depth = null;
    public byte[][] floor = null;
}

public class ResetMessage {
    public float reward = 0.0F;
    public int success = 0;
    public int failure = 0;
    public int elapsed = 0;
    public bool finished = false;
}
