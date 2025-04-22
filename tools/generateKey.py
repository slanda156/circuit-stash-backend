from rsa import newkeys

print("Starting...")

pub, prv = newkeys(256)

print("Saving...")

with open("secrets/public.key", "wb") as f:
    f.write(pub.save_pkcs1())

with open("secrets/private.key", "wb") as f:
    f.write(prv.save_pkcs1())

print("Done!")
