from lepton_utils import LeptonCamera


def run():
    #raw_dir = "~/Biomaker/Biomaker_2020/control_software/image_capture/raw_imgs"
    #img_dir = "~/Biomaker/Biomaker_2020/control_software/image_capture/imgs"
    raw_dir = "raw_imgs/"
    img_dir = "imgs/"
    lepcam = LeptonCamera(raw_dir, img_dir)
    lepcam.preview()


if __name__ == "__main__":
    run()
