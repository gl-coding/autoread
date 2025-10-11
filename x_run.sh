function gen_pdf() {
    #先清空目录，裁剪目录
    rm -rf cropped
    #再清空分割目录
    rm -rf split_results
    #再清空ocr目录
    #rm -rf ocr_results

    # 裁剪图片，去掉电脑背景的边框，保留书本的内容
    python batch_crop.py

    # 分割图片，将书本分割为左右两部分
    python image_split.py --batch cropped split_results

    # 识别图片，将左右两部分图片识别为文字，并合并为pdf
    # python images_to_pdf.py

    # mv output/output.pdf ~/Downloads

    # open ~/Downloads
}

function auto_read(){
    #先开启微信阅读，打开相应的书，然后运行这个脚本，截图保存在screenshots目录
    python mouse_tracker.py
}

function ocr(){
    python ocr_tesseract.py
}

arg=$1
case $arg in
    "gen")
        gen_pdf
        ;;
    "ocr")
        ocr
        ;;
    "auto")
        auto_read
        ;;
    *)
        echo "Usage: $0 {gen_pdf}"
        ;;
esac