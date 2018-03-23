class Range {
    public float start;
    public float end;

    Range(float _start, float _end) {
        start = _start;
        end = _end;
    }

    public static Range Red   = new Range(17.5F, 21.5F);
    public static Range Green = new Range(11.5F, 15.5F);
    public static Range Blue  = new Range(5.5F, 9.5F);
}
