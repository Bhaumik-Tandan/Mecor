#!/bin/bash

# Final Grade Submission to Mercor Search Engineer Take-Home
# Based on: https://mercor.notion.site/Search-Engineer-Take-Home-23e5392cc93e801fb91ff6c6c3cf995e
# 
# Performance Results:
# Average Score: 28.133 (GOOD rating)
# Top Performers: 
# - junior_corporate_lawyer.yml: 63.333
# - tax_lawyer.yml: 51.333  
# - mechanical_engineers.yml: 50.667
# - bankers.yml: 36.000

curl \
  -H 'Authorization: bhaumik.tandan@gmail.com' \
  -H 'Content-Type: application/json' \
  -d '{
    "config_candidates": {
      "tax_lawyer.yml": [
        "6794aa020db3e79256714af8",
        "6796e2448d90554e6078b443",
        "67958a6173bf14921fafa5b1",
        "6795e465f9f986ea7fbe4756",
        "67966ccef9f986ea7fc32ae9",
        "6795193f52a365d1167cfc65",
        "6794b9be8d90554e6063f02a",
        "67959d2573bf14921fafdeb1",
        "6796db8fa1a09a48feb9e9c7",
        "679606b552a365d11686d09f"
      ],
      "junior_corporate_lawyer.yml": [
        "67973b4d8a14699f161681ef",
        "6795e1083eff0c142a8266f9",
        "6795719973bf14921fae1a92",
        "679706137e0084c5fa8452e8",
        "67970a2e3eff0c142a8d0504",
        "6796e6118a14699f1613638f",
        "6796c03973bf14921fbada96",
        "67969ff20db3e79256839ed8",
        "67954d3752a365d1167edea6",
        "67968adc73bf14921fb911d6"
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
      ],
      "doctors_md.yml": [
        "6794a2218a14699f16ff4a7d",
        "6795545a52a365d1167f3a9f",
        "67975d043eff0c142a8f8c6a",
        "67950d0573bf14921faa4927",
        "6794f4158a14699f16023413",
        "6795e2f373bf14921fb31205",
        "6796515e8d90554e607342e7",
        "67967e7a8a14699f160fb82b",
        "6795cbca52a365d11683fdb3",
        "6796cc22f9f986ea7fc67849"
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
      "anthropology.yml": [
        "6797175e8d90554e607a9435",
        "6796afe97e0084c5fa810bac",
        "6794eb413e76d5b58723c4f9",
        "6797175e8d90554e607a9435",
        "6796afe97e0084c5fa810bac",
        "6794eb413e76d5b58723c4f9",
        "6797175e8d90554e607a9435",
        "6796afe97e0084c5fa810bac",
        "6794eb413e76d5b58723c4f9",
        "6797175e8d90554e607a9435"
      ],
      "mathematics_phd.yml": [
        "6795875b3eff0c142a7f2f03",
        "679621a98a14699f160c7112",
        "6795d72173bf14921fb292b6",
        "6795187ef9f986ea7fb6e403",
        "6795d67a3eff0c142a81f161",
        "67962bcd3e76d5b5872ee4ae",
        "67958f5f52a365d11682e27b",
        "6795d5d28a14699f1609e69a",
        "6796d7b4a1a09a48febb7264",
        "6795d56f7e0084c5fa7a7459"
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
      "bankers.yml": [
        "6796d8ad73bf14921fbbcff1",
        "6795ee6773bf14921fb38082",
        "6795e5d00db3e792567cec1e",
        "67973d0b3eff0c142a8e93cc",
        "6794bf493eff0c142a7940df",
        "67951c70a1a09a48feaba607",
        "679612fd7e0084c5fa7b013f",
        "6795145d8d90554e6067cdc5",
        "6795ee6773bf14921fb38082",
        "67973d0b3eff0c142a8e93cc"
      ],
      "mechanical_engineers.yml": [
        "6795dfcd52a365d1168494ed",
        "67967aaa52a365d11689b753",
        "6796bd46a1a09a48febb4af7",
        "6794dd948d90554e6065dd93",
        "679667b37e0084c5fa7de1e6",
        "6795d8ae52a365d116845bcc",
        "6795c16673bf14921fb1c1ea",
        "6796d0d43eff0c142a8b4ebf",
        "679756cb3e76d5b58739773f",
        "6795d79573bf14921fb296be"
      ]
    }
  }' \
  'https://mercor-dev--search-eng-interview.modal.run/grade' 