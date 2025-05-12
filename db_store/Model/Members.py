class Members(db.Model):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone_number = Column(String(20))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    update_at= Column(DateTime, default=datetime.utcnow)

    # backref from CallTreeEntry and NotificationRecipient
   #call_tree_entries = relationship('CallTreeEntry', back_populates='recipient', cascade='all, delete-orphan')
    #notifications = relationship('NotificationRecipient', back_populates='recipient', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Members {self.id} {self.name}>"