# OKE Troubleshooting

## kubectl 401 Unauthorized
Session token expired. Re-authenticate:
```bash
oci session authenticate --region me-dubai-1 --profile-name OKE_SESSION
```

## exec plugin apiVersion mismatch (v1beta1 vs v1)
Already resolved. Wrapper at `~/.oci/oke-token.sh` converts OCI CLI v1beta1 output to v1 for kubectl v1.35+. If kubeconfig is regenerated, re-apply:
- Set `apiVersion: client.authentication.k8s.io/v1` in exec block
- Set `command: /home/safdarayub/.oci/oke-token.sh`
- Set `args:` to cluster OCID and region
- Add `interactiveMode: Never`

## Image pull errors
Images are public on Docker Hub. No imagePullSecret needed. Verify: `docker pull safdarayub/todo-backend:v3-complete`

## Node not ready
```bash
oci ce node-pool get --node-pool-id ocid1.nodepool.oc1.me-dubai-1.aaaaaaaa74b2l55tnadwhmmilsjis6f3kvhjwwee6zope2hijnjkcvcumrhq --query "data.nodes[].\"lifecycle-state\"" --auth security_token --profile OKE_SESSION
```

## OCI CLI 401 NotAuthenticated
Check API key fingerprint matches console. Test: `oci os ns get`

## Pod CrashLoopBackOff
```bash
kubectl logs <pod-name> --previous
kubectl describe pod <pod-name>
```

## ARM vs x86 mismatch
Docker images are x86/amd64. Do NOT use VM.Standard.A1.Flex (ARM) without rebuilding images for arm64.
