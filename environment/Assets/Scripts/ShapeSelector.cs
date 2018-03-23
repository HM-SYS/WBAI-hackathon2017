using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof (Image))]
public class ShapeSelector : MonoBehaviour {
    public Sprite[] Shapes;
    public int Selection = 0;
    public bool Visible = true;
    public Image image;

    void Update () {
        image.sprite = Shapes[Selection];

        if(!Visible) {
            Destroy(gameObject);
        }
    }
}
