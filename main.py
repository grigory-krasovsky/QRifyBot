import base64
from io import BytesIO
import requests
import qrcode
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext

CLIENT_ID = '9d3a363f8e1dfda4efc3207da17462a2'
URL = "https://api.imgbb.com/1/upload?key=" + CLIENT_ID
TOKEN = '6896121180:AAE3ANCpdbHxUIICDA_iqd1fEDXseSW26to'


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! Send me a photo, and I will generate a QR code for it.')


def upload_to_hosting(image_bytes) -> str:

    encoded_image = base64.b64encode(image_bytes.getvalue()).decode('utf-8')
    print('encoded_image')
    print(encoded_image)
    response = requests.post(URL, data={"image": encoded_image})
    img_url = response.json()["data"]["url"]
    print(img_url)
    return img_url


def handle_message(update: Update, context: CallbackContext) -> None:
    # Check if the update contains a photo
    if update.message.photo:
        # Get the photo from the message
        photo = update.message.photo[-1]
        photo_file = photo.get_file()
        photo_bytes = BytesIO()
        photo_file.download(out=photo_bytes)
        photo_bytes.seek(0)

        # Upload the image to Imgur and get the URL
        try:
            imgur_url = upload_to_hosting(photo_bytes)
        except Exception as e:
            update.message.reply_text(f"Failed to upload image to Imgur: {e}")
            return

        # Generate a QR code with the image URL
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(imgur_url)
        qr.make(fit=True)
        img_qr = qr.make_image(fill='black', back_color='white')

        # Save the QR code to a bytes object
        bio = BytesIO()
        img_qr.save(bio, format='PNG')
        bio.seek(0)

        # Send the QR code back to the user
        update.message.reply_photo(photo=bio)
    else:
        update.message.reply_text('Please send a photo.')


def main() -> None:
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(None, handle_message))

    updater.start_polling()
    print('Bot started polling')
    updater.idle()


if __name__ == '__main__':
    main()
