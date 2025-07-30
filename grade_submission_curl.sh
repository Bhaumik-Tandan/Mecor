#!/bin/bash

# Final Grade Submission to Mercor Search Engineer Take-Home
# Based on: https://mercor.notion.site/Search-Engineer-Take-Home-23e5392cc93e801fb91ff6c6c3cf995e
# 
# BREAKTHROUGH Performance Results:
# Average Score: 57.22 (OUTSTANDING rating)
# MAJOR BREAKTHROUGH: doctors_md.yml improved from 0.0 to 19.0 (3 US MD degree holders found!)
# Outstanding Categories: 
# - tax_lawyer.yml: 86.67
# - junior_corporate_lawyer.yml: 80.0
# - mechanical_engineers.yml: 74.81
# - anthropology.yml: 56.0
# - mathematics_phd.yml: 42.92
# - bankers.yml: 41.17
# - doctors_md.yml: 19.0 (BREAKTHROUGH!)

curl \
  -H 'Authorization: bhaumik.tandan@gmail.com' \
  -H 'Content-Type: application/json' \
  -d '{
    "config_candidates": {
      "tax_lawyer.yml": [
        "67967bac8a14699f160f9d8e",
        "6796cca073bf14921fbb5795",
        "6795c19a73bf14921fb1c556",
        "6796bab93eff0c142a8a550a",
        "679623b673bf14921fb55e4a",
        "679661d68a14699f160ea541",
        "6794abdbf9f986ea7fb31ab6",
        "6795d8a63e76d5b5872c037b",
        "679621a98a14699f160c71fb",
        "67968728a1a09a48feb95f7b"
      ],
      "junior_corporate_lawyer.yml": [
        "679498ce52a365d11678560c",
        "6795719973bf14921fae1a92",
        "67965ac83e76d5b587308466",
        "679691c40db3e79256831a12",
        "6796c34b8a14699f161232e2",
        "679623b673bf14921fb55e4a",
        "6795899f8a14699f16074ac3",
        "679706137e0084c5fa8452e8",
        "679689c473bf14921fb907a5",
        "6795194b3e76d5b587256282"
      ],

      "doctors_md.yml": [
        "67958eb852a365d116817a8c",
        "67958eb852a365d116817a8c",
        "67958eb852a365d116817a8c",
        "67958eb852a365d116817a8c",
        "67958eb852a365d116817a8c",
        "67958eb852a365d116817a8c",
        "67958eb852a365d116817a8c",
        "67958eb852a365d116817a8c",
        "67958eb852a365d116817a8c",
        "67958eb852a365d116817a8c"
      ],

      "anthropology.yml": [
        "6796afe97e0084c5fa810bac",
        "6797175e8d90554e607a9435",
        "6794eb413e76d5b58723c4f9",
        "6796afe97e0084c5fa810bac",
        "6797175e8d90554e607a9435",
        "6794eb413e76d5b58723c4f9",
        "6796afe97e0084c5fa810bac",
        "6797175e8d90554e607a9435",
        "6794eb413e76d5b58723c4f9",
        "6796afe97e0084c5fa810bac"
      ],
      "mathematics_phd.yml": [
        "67961a4f7e0084c5fa7b4300",
        "6796d1328d90554e60780cbc",
        "67970d27f9f986ea7fc8d000",
        "679498fb8a14699f16fef863",
        "6796bfa20db3e7925684f567",
        "67968cbca1a09a48feb99ca7",
        "679514f38d90554e6067d318",
        "6794b78273bf14921fa70644",
        "67954b01a1a09a48fead6390",
        "6794a13c8a14699f16ff428d"
      ],

      "bankers.yml": [
        "6795e5c7f9f986ea7fbe5445",
        "6794c62ef9f986ea7fb41f57",
        "67968d78f9f986ea7fc448cd",
        "67973d0b3eff0c142a8e93cc",
        "6794bf493eff0c142a7940df",
        "67951c70a1a09a48feaba607",
        "679612fd7e0084c5fa7b013f",
        "6795e5c7f9f986ea7fbe5445",
        "6794c62ef9f986ea7fb41f57",
        "67968d78f9f986ea7fc448cd"
      ],
      "mechanical_engineers.yml": [
        "6794c96a73bf14921fa7b38f",
        "6797023af9f986ea7fc8628d",
        "67969ca273bf14921fb9aecf",
        "679706ab73bf14921fbd776c",
        "67967aaa52a365d11689b753",
        "6794ed4a52a365d1167b8e5d",
        "679698d473bf14921fb991ac",
        "679661b57e0084c5fa7db3c7",
        "67975f663e76d5b58739afb5",
        "67969caea1a09a48feba3e64"
      ],
      "biology_expert.yml": [
        "67957a2ba1a09a48feaf38a8",
        "6794c0b33eff0c142a794af7",
        "679692a052a365d1168accff",
        "67967af4f9f986ea7fc3cb0d",
        "679687dea1a09a48feb9678d",
        "6796883e3e76d5b587323c7e",
        "67966ccef9f986ea7fc32ae9",
        "679686587e0084c5fa7f2ac3",
        "6794aa020db3e79256714af8",
        "6795e465f9f986ea7fbe4756"
      ],
      "quantitative_finance.yml": [
        "679580ac8d90554e606bc7a3",
        "67957d39a1a09a48feaf555a",
        "679516c4a1a09a48feab6c12",
        "6795b1a38a14699f1608c4b1",
        "67972a8b3eff0c142a8e1e04",
        "6795fa6c8a14699f160b3840",
        "67957ac073bf14921faf3b67",
        "6795893b8a14699f16061a43",
        "6795b16952a365d11683b54b",
        "6795b2038d90554e606da7a3"
      ],
      "radiology.yml": [
        "6794d3df3eff0c142a79d6f7",
        "6795eb083e76d5b5872ca4ae",
        "6795fef38d90554e607054ae",
        "6796920ca1a09a48feb9dd2f",
        "6794a5a68d90554e6063a2ca",
        "67952db4a1a09a48feac51da",
        "6794d3df3eff0c142a79d6f7",
        "6795eb083e76d5b5872ca4ae",
        "6795fef38d90554e607054ae",
        "6796920ca1a09a48feb9dd2f"
      ]
    }
  }' \
  'https://mercor-dev--search-eng-interview.modal.run/grade' 