![S-SPHAR Synthetic Surveillance Perspective Human Action Recognition Logo](docs/S-SPHAR.svg)

# **S-SPHAR**: **S**ynthetic **S**urveillance **P**erspective **H**uman **A**ction **R**ecognition **D**ataset


**S-SPHAR** is a synthetically generated video dataset for human action recognition. Its main purpose is to support research in the application area of analyzing activities on public places.

In this domain, most cameras will share a similar mounting angle and perspective, which we will call the **surveillance perspective** from now on. In **S-SPHAR**, all videos are shot from this or a similar perspective.

The videos have been generated using a self-made simulation built using the Unity game engine and characters and animations from Mixamo.

This Repository contains all videos of the **S-SPHAR** dataset.

-----------

Looking for the non-synthetic SPHAR-Dataset? [Click here](https://github.com/AlexanderMelde/SPHAR-Dataset)

-----------


## Dataset Overview

| Dataset Version | # Videos |  # Classes | Videos per Class |  Dataset Size | Original Video Length | Original Video Size | Year |
|-----------------|----------|------------|------------------|---------------|-----------------------|---------------------|------|
|               1 |      260 |  9  (HMDB) |           8 - 92 |         40 MB |             02:36 min |              860 MB | 2020 |
|               2 |      696 | 10 (SPHAR) |          3 - 236 |        168 MB |             09:04 min |             4.01 GB | 2020 |
|               3 |     6901 | 10 (SPHAR) |        42 - 2328 |       1.03 GB |             48:22 min |             12.9 GB | 2020 |

## Original Videos
Due to their size, the original videos were not uploaded to GitHub. Instead, they can be found at YouTube under the following links. Read their descriptions for more information:

- [S-SPHAR-3](https://youtu.be/ybFYFRJoQho)
- [S-SPHAR-2](https://youtu.be/3x8ga83Cm1k)
- [S-SPHAR-1](https://youtu.be/64NR86A3tGU)

[![preview image of S-SPHAR videos](https://img.youtube.com/vi/ybFYFRJoQho/mqdefault.jpg)](https://youtu.be/ybFYFRJoQho)

Those Videos are combinations of the following video views:
- Original camera image
- Segmentation masks for labeled action classes
- Overlay of segmentation masks over original camera image
- Bounding boxes around action instance tubes

The videos are all 4K resolution, so you can split it back into four FHD videos using simple tools like OpenCV or other video editors.


## Download
The easiest way to just get the cropped dataset videos is by downloading one of our [releases](https://github.com/AlexanderMelde/S-SPHAR-Dataset/releases):

- [**S-SPHAR-Dataset-R1.0.zip**](https://github.com/AlexanderMelde/S-SPHAR-Dataset/archive/R1.0.zip)

You can also clone or fork this repository using:

```
git clone git@github.com:AlexanderMelde/S-SPHAR-Dataset.git
```

If you want to download the original videos, use the links above and a YouTube downloader like [youtube-dl](https://github.com/ytdl-org/youtube-dl).

## License
The **S-SPHAR Dataset** is released under the **GNU GPL v3** license (contact me for further licensing options).

See the [LICENSE](LICENSE) file for more details.

## Citation
If you want to cite and reference the **S-SPHAR Dataset**, please link to this GitHub page. You can use the following BibTex entry:

```bib
@article{s-sphar-dataset,
  title={S-SPHAR: Surveillance Perspective Human Action Recognition Dataset},
  author={Alexander Melde},
  year={2020},
  publisher = {GitHub},
  journal = {GitHub repository},
  url = {https://github.com/AlexanderMelde/S-SPHAR-Dataset},
  version = {\UrlFont\href{https://github.com/AlexanderMelde/S-SPHAR-Dataset/commit/4e5a493}{4e5a493}},
  urldate={2020-09-29}
}
```
(replace urldate with your own day of retrieval)
