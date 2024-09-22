from oidc_provider.lib.claims import ScopeClaims

def userinfo(claims, user):
    """
    Custom user info to include in the OpenID Connect token.
    """
    claims['name'] = user.get_full_name() or user.username
    claims['email'] = user.email
    claims['preferred_username'] = user.username
    claims['sub'] = str(user.id)

    if hasattr(user, 'customer'):
        claims['customer_id'] = str(user.customer.id)
        claims['customer_code'] = user.customer.code

    return claims

class CustomScopeClaims(ScopeClaims):
    """
    Custom claims class to add extra information for the 'customer' scope.
    """
    info_customer = (
        "Customer details of the logged-in user, "
        "like customer ID or associated data."
    )

    def scope_customer(self):
        """
        Return extra information for the 'customer' scope.
        Available only if the 'customer' scope is requested.
        """
        if hasattr(self.user, 'customer'):
            return {
                'customer_id': str(self.user.customer.id),
                'customer_code': self.user.customer.code,
            }
        return {}
