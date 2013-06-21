#!/usr/bin/python
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

from pystruct.utils import SaveLogger
from datasets import PascalSegmentation

from pascal.pascal_helpers import load_pascal
from utils import add_edges, add_edge_features, eval_on_pixels


def main():
    argv = sys.argv
    print("loading %s ..." % argv[1])
    ssvm1 = SaveLogger(file_name=argv[1]).load()
    ssvm2 = SaveLogger(file_name=argv[2]).load()

    data_str = 'val'
    if len(argv) <= 3:
        raise ValueError("Need a folder name for plotting.")
    print("loading data...")
    data = load_pascal(data_str)
    dataset = PascalSegmentation()
    print("done")
    data1 = add_edges(data, independent=False)
    data2 = add_edges(data, independent=True)
    data1 = add_edge_features(data1)
    #data2 = add_edge_features(data2)
    Y_pred1 = ssvm1.predict(data1.X)
    Y_pred2 = ssvm2.predict(data2.X)
    folder = argv[3]

    if not os.path.exists(folder):
        os.mkdir(folder)

    np.random.seed(0)
    for image_name, superpixels, y_pred1, y_pred2 in zip(data.file_names,
                                                         data.superpixels,
                                                         Y_pred1, Y_pred2):
        if np.all(y_pred1 == y_pred2):
            continue
        image = dataset.get_image(image_name)
        fig, axes = plt.subplots(2, 3, figsize=(12, 6))
        axes[0, 0].imshow(image)
        axes[0, 0].imshow((y_pred1 != y_pred2)[superpixels], vmin=0, vmax=1,
                          alpha=.7)

        axes[0, 1].set_title("ground truth")
        axes[0, 1].imshow(image)
        gt = dataset.get_ground_truth(image_name)
        axes[0, 1].imshow(gt, alpha=.7, cmap=dataset.cmap)
        perf = eval_on_pixels([gt], [y_pred1[superpixels]],
                              print_results=False)[0]
        perf = np.mean(perf[np.isfinite(perf)])
        axes[1, 0].set_title("%.2f" % perf)
        axes[1, 0].imshow(image)
        axes[1, 0].imshow(y_pred1[superpixels], vmin=0, alpha=.7,
                          cmap=dataset.cmap)

        perf = eval_on_pixels([gt], [y_pred2[superpixels]],
                              print_results=False)[0]
        perf = np.mean(perf[np.isfinite(perf)])
        axes[1, 1].set_title("%.2f" % perf)
        axes[1, 1].imshow(image)
        axes[1, 1].imshow(y_pred2[superpixels], alpha=.7, cmap=dataset.cmap)
        present_y = np.unique(np.hstack([y_pred1, y_pred2]))
        axes[0, 2].imshow(present_y[np.newaxis, :], interpolation='nearest',
                          cmap=dataset.cmap)
        for i, c in enumerate(present_y):
            axes[0, 2].text(1, i, dataset.classes[c])
        for ax in axes.ravel():
            ax.set_xticks(())
            ax.set_yticks(())
        axes[1, 2].set_visible(False)
        fig.savefig(folder + "/%s.png" % image_name, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    main()
