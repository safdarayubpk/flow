# OKE Infrastructure OCIDs

## OCI Account
| Key | Value |
|---|---|
| Region | me-dubai-1 |
| Tenancy OCID | ocid1.tenancy.oc1..aaaaaaaauja2v57o6tjty473i7hvj3owqheagpmsdxc7jo2nc7yli5ipvuyq |
| Namespace | axl9oh0mzzj5 |
| User | safdarayub@gmail.com |
| User OCID | ocid1.user.oc1..aaaaaaaakpi7cwpj3tfw5bsnbquwvd3arwyymtxuoeoakd2yhnirn5jxrheq |
| API Key Fingerprint | be:eb:9e:7f:4a:0c:a6:45:9b:8e:c4:41:97:41:f4:b2 |

## OKE Cluster
| Key | Value |
|---|---|
| Cluster Name | todo-oke-cluster |
| Cluster OCID | ocid1.cluster.oc1.me-dubai-1.aaaaaaaag2nmeu5aworqfjb7bussqszpnvo3kp4tqlms5sj3sciwo4wljedq |
| K8s Version | v1.32.1 |
| Type | BASIC_CLUSTER |
| API Endpoint | https://139.185.40.234:6443 |

## Node Pool
| Key | Value |
|---|---|
| Node Pool OCID | ocid1.nodepool.oc1.me-dubai-1.aaaaaaaa74b2l55tnadwhmmilsjis6f3kvhjwwee6zope2hijnjkcvcumrhq |
| Shape | VM.Standard.E2.1 (1 OCPU, 8GB, x86) |
| Nodes | 1 |
| AD | htHs:ME-DUBAI-1-AD-1 |
| Image | Oracle Linux 8.10 OKE 1.32.1 |
| Internal IP | 10.0.1.82 |
| External IP | 141.145.148.16 |

## Networking
| Resource | OCID | CIDR |
|---|---|---|
| VCN (todovcn) | ocid1.vcn.oc1.me-dubai-1.amaaaaaakcltcgqawgxbbtlfifwn6gt3rbxz3v3fg4bht3ith2awkotj32vq | 10.0.0.0/16 |
| API Subnet | ocid1.subnet.oc1.me-dubai-1.aaaaaaaa34mwe55fjhrzo4bbwm7yvugquflrgwutxoiy35jzwoah6n6mhnba | 10.0.0.0/24 |
| Node Subnet | ocid1.subnet.oc1.me-dubai-1.aaaaaaaaz2wh7mnyxszwt46u5cyl4s46626on7oypa2zooi6rnn3curtlexa | 10.0.1.0/24 |
| LB Subnet | ocid1.subnet.oc1.me-dubai-1.aaaaaaaasbvbt52uox37vywgrqmv3pawnznopr43syql5z6qviepthuk7qua | 10.0.2.0/24 |
| Internet GW | ocid1.internetgateway.oc1.me-dubai-1.aaaaaaaajnyls6xnu2uf4s737jgc5flf4vebsz3mskfbqlc6opg65tw4odbq | — |
| Service GW | ocid1.servicegateway.oc1.me-dubai-1.aaaaaaaa5oqyt26hmo6xze2xguc2em2pnzh27ftem6mgtyvzx54ltgbsiiuq | — |
