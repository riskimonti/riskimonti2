import hashlib

def generate_unique_image_name(image_name):
    # Create a hash object
    hash_object = hashlib.sha256()

    # Convert the image name to bytes and update the hash object
    hash_object.update(image_name.encode('utf-8'))

    # Generate the unique image name by digesting the hash
    unique_name = hash_object.hexdigest()

    return unique_name
